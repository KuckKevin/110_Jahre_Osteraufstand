#Diese Dateie dokumentiert den gescheiterten Versuch,
#verschiedene Nachrichtenseiten gleichzeitig zu scrapen.
#Versucht NICHT den kompletten Code zu verstehen.



"""
Multi-source article collector for Easter Rising coverage.

Ziel:
- Vier Seiten durchsuchen:
  - Irish Times
  - BBC
  - RTÉ
  - An Phoblacht
- Pro Artikel sammeln:
  - Quelle
  - Suchbegriff
  - Titel
  - URL
  - Erscheinungsdatum
  - Autor
  - Teaser / Summary
  - Volltext
  - Abrufzeitpunkt
- Ausgabe als JSON

Hinweise:
- Primär wird requests genutzt; Selenium ist optional als Fallback einbaubar.
- Suchseiten sind je Website unterschiedlich; deshalb gibt es kleine Adapter.
- Die Extraktion des Artikeltexts ist möglichst generisch und nutzt Meta-Tags,
  JSON-LD und heuristische Textgewinnung.
- Nicht jede Website wird dauerhaft mit unveränderten Such-URLs/DOM-Strukturen
  funktionieren; das Skript ist absichtlich so gebaut, dass sich die Adapter
  leicht anpassen lassen.

Python 3.10+
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable, Optional
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


# =========================
# Configuration
# =========================

QUERY = "Easter Rising"
MAX_RESULTS_PER_SITE = 10
REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_REQUESTS = 1.0
OUTPUT_FILE = "easter_rising_articles.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9,de;q=0.8",
}


# =========================
# Data model
# =========================

@dataclass
class Article:
    source: str
    query: str
    title: str
    url: str
    date_published: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    article_text: Optional[str] = None
    search_url: Optional[str] = None
    scraped_at: Optional[str] = None
    status: str = "ok"
    error: Optional[str] = None


@dataclass
class SearchResult:
    source: str
    query: str
    title: str
    url: str
    date_published: Optional[str] = None
    search_url: Optional[str] = None


@dataclass
class SiteConfig:
    name: str
    domain: str
    search_url_template: Optional[str]
    allowed_domains: tuple[str, ...]
    blocked_url_patterns: tuple[str, ...] = ()
    preferred_search_container_selectors: tuple[str, ...] = ()
    article_path_hints: tuple[str, ...] = ()
    requires_js: bool = False


# =========================
# Site definitions
# =========================

SITES: list[SiteConfig] = [
    SiteConfig(
        name="Irish Times",
        domain="www.irishtimes.com",
        search_url_template="https://www.irishtimes.com/search/?query={query}",
        allowed_domains=("www.irishtimes.com", "irishtimes.com"),
        blocked_url_patterns=(
            "/search/",
            "/video/",
            "/podcasts/",
            "/crosswords/",
            "/games/",
            "/privacy",
            "/terms",
            "/account",
            "/subscribe",
            "/about-us",
            "/archive",
            "/discounts",
            "/notices",
            "/sport/six-nations",
        ),
        preferred_search_container_selectors=(
            "div.queryly_item_row",
            "article",
            ".search-results article",
            ".search-result",
        ),
        article_path_hints=("/",),
    ),
    SiteConfig(
        name="BBC",
        domain="www.bbc.co.uk",
        search_url_template="https://www.bbc.co.uk/search?q={query}",
        allowed_domains=("www.bbc.co.uk", "bbc.co.uk", "www.bbc.com", "bbc.com"),
        blocked_url_patterns=(
            "/search",
            "/sounds/",
            "/iplayer/",
            "/programmes/",
            "/bitesize/",
            "/newsround/",
            "/sport/",
            "/weather/",
            "/accounts",
            "/contact",
        ),
        preferred_search_container_selectors=(
            "main article",
            "article",
            "[data-testid='newport-search-result']",
        ),
        article_path_hints=("/news/", "/programmes/", "/archive/"),
    ),
    SiteConfig(
        name="RTÉ",
        domain="www.rte.ie",
        search_url_template="https://www.rte.ie/search/query/{query}/",
        allowed_domains=("www.rte.ie", "rte.ie"),
        blocked_url_patterns=(
            "/search/query/",
            "/radio/",
            "/player/",
            "/sport/",
            "/brainstorm/",
            "/lifestyle/",
            "/gaeilge/",
            "/contact",
        ),
        preferred_search_container_selectors=(
            "article",
            ".search-results article",
            ".search-result",
            ".o-teaser",
        ),
        article_path_hints=("/news/", "/culture/", "/history/", "/centuryireland/"),
    ),
    SiteConfig(
        name="An Phoblacht",
        domain="www.anphoblacht.com",
        # Falls die Such-URL sich ändert, hier anpassen.
        # Alternativ kann None gesetzt werden, dann wird die Startseite als Seed benutzt.
        search_url_template="https://www.anphoblacht.com/search?query={query}",
        allowed_domains=("www.anphoblacht.com", "anphoblacht.com"),
        blocked_url_patterns=(
            "/contact",
            "/about",
            "/polls",
            "/login",
            "/register",
        ),
        preferred_search_container_selectors=(
            "article",
            ".article",
            ".story",
            ".post",
        ),
        article_path_hints=("/contents/",),
    ),
]


# =========================
# HTTP / HTML helpers
# =========================

session = requests.Session()
session.headers.update(HEADERS)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_html(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def safe_get_text(el: Optional[Tag]) -> Optional[str]:
    if not el:
        return None
    text = el.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip() or None


def normalize_url(url: str, base_url: str) -> str:
    if not url:
        return url
    url = urljoin(base_url, url)
    parsed = urlparse(url)
    clean = parsed._replace(fragment="").geturl()
    return clean


def domain_allowed(url: str, site: SiteConfig) -> bool:
    netloc = urlparse(url).netloc.lower()
    return any(netloc == domain or netloc.endswith("." + domain) for domain in site.allowed_domains)


def url_blocked(url: str, site: SiteConfig) -> bool:
    lower = url.lower()
    return any(pattern.lower() in lower for pattern in site.blocked_url_patterns)


def looks_like_asset(url: str) -> bool:
    lower = url.lower()
    return lower.endswith((
        ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
        ".pdf", ".zip", ".mp3", ".mp4", ".avi", ".mov"
    ))


def tokenize_query(query: str) -> list[str]:
    return [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]


# =========================
# JSON-LD / metadata helpers
# =========================

def parse_json_ld(soup: BeautifulSoup) -> list[dict]:
    items: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except Exception:
            continue

        if isinstance(parsed, dict):
            if "@graph" in parsed and isinstance(parsed["@graph"], list):
                items.extend([x for x in parsed["@graph"] if isinstance(x, dict)])
            else:
                items.append(parsed)
        elif isinstance(parsed, list):
            items.extend([x for x in parsed if isinstance(x, dict)])
    return items


def extract_author(author_field) -> Optional[str]:
    if isinstance(author_field, str):
        return author_field.strip() or None
    if isinstance(author_field, dict):
        return author_field.get("name")
    if isinstance(author_field, list):
        names = []
        for item in author_field:
            if isinstance(item, str):
                names.append(item.strip())
            elif isinstance(item, dict) and item.get("name"):
                names.append(str(item["name"]).strip())
        return ", ".join(n for n in names if n) or None
    return None


def extract_date_from_meta(soup: BeautifulSoup) -> Optional[str]:
    candidates = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "article:published_time"}),
        ("meta", {"name": "pubdate"}),
        ("meta", {"name": "publish-date"}),
        ("meta", {"name": "publication_date"}),
        ("meta", {"name": "date"}),
        ("meta", {"itemprop": "datePublished"}),
        ("time", {"datetime": True}),
    ]
    for name, attrs in candidates:
        el = soup.find(name, attrs=attrs)
        if not el:
            continue
        if name == "time":
            return el.get("datetime")
        content = el.get("content")
        if content:
            return content.strip()
    return None


def extract_title_from_meta(soup: BeautifulSoup) -> Optional[str]:
    candidates = [
        ("meta", {"property": "og:title"}),
        ("meta", {"name": "twitter:title"}),
        ("meta", {"itemprop": "headline"}),
    ]
    for name, attrs in candidates:
        el = soup.find(name, attrs=attrs)
        if el and el.get("content"):
            return el["content"].strip()
    if soup.title:
        return safe_get_text(soup.title)
    return None


def extract_summary_from_meta(soup: BeautifulSoup) -> Optional[str]:
    candidates = [
        ("meta", {"property": "og:description"}),
        ("meta", {"name": "description"}),
        ("meta", {"name": "twitter:description"}),
    ]
    for name, attrs in candidates:
        el = soup.find(name, attrs=attrs)
        if el and el.get("content"):
            return el["content"].strip()
    return None


def extract_author_from_meta(soup: BeautifulSoup) -> Optional[str]:
    candidates = [
        ("meta", {"name": "author"}),
        ("meta", {"property": "article:author"}),
        ("meta", {"itemprop": "author"}),
    ]
    for name, attrs in candidates:
        el = soup.find(name, attrs=attrs)
        if el and el.get("content"):
            return el["content"].strip()
    return None


# =========================
# Text extraction
# =========================

def clean_text_block(text: str) -> str:
    text = re.sub(r"\u00a0", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def score_text_container(tag: Tag) -> int:
    paragraphs = tag.find_all("p")
    p_count = len(paragraphs)
    text_len = sum(len(p.get_text(" ", strip=True)) for p in paragraphs)
    score = p_count * 20 + min(text_len, 5000) // 25

    class_and_id = " ".join(tag.get("class", [])) + " " + (tag.get("id") or "")
    lowered = class_and_id.lower()
    bonuses = [
        "article", "story", "content", "main", "body", "entry", "post", "text"
    ]
    penalties = [
        "footer", "header", "nav", "related", "promo", "advert", "sidebar", "share"
    ]
    for b in bonuses:
        if b in lowered:
            score += 25
    for p in penalties:
        if p in lowered:
            score -= 30
    return score


def extract_article_text(soup: BeautifulSoup) -> Optional[str]:
    candidates: list[Tag] = []

    article = soup.find("article")
    if article:
        candidates.append(article)

    main = soup.find("main")
    if main:
        candidates.append(main)

    for selector in [
        "[itemprop='articleBody']",
        ".article-body",
        ".story-body",
        ".article-content",
        ".entry-content",
        ".post-content",
        ".content",
    ]:
        for el in soup.select(selector):
            if isinstance(el, Tag):
                candidates.append(el)

    candidates = list(dict.fromkeys(candidates))  # dedupe while preserving order

    best_text = None
    best_score = -1

    for candidate in candidates:
        paragraphs = candidate.find_all("p")
        parts = []
        for p in paragraphs:
            text = p.get_text(" ", strip=True)
            if not text:
                continue
            if len(text) < 30:
                continue
            parts.append(text)
        joined = "\n".join(parts).strip()
        if not joined:
            continue
        score = score_text_container(candidate)
        if score > best_score:
            best_score = score
            best_text = joined

    if best_text:
        return clean_text_block(best_text)

    # fallback: all meaningful paragraphs on the page
    parts = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) >= 40:
            parts.append(text)
    if parts:
        return clean_text_block("\n".join(parts))

    return None


def looks_like_article_page(url: str, title: Optional[str], article_text: Optional[str]) -> bool:
    if not title or not article_text:
        return False
    if len(title) < 8:
        return False
    if len(article_text) < 250:
        return False
    lower = url.lower()
    junk = ["/tag/", "/tags/", "/search", "/topic/", "/topics/", "/live/"]
    if any(j in lower for j in junk):
        return False
    return True


# =========================
# Search result extraction
# =========================

def find_candidate_link_containers(soup: BeautifulSoup, site: SiteConfig) -> list[Tag]:
    containers: list[Tag] = []
    for selector in site.preferred_search_container_selectors:
        found = soup.select(selector)
        if found:
            containers.extend([x for x in found if isinstance(x, Tag)])
    if containers:
        return containers

    # fallback: use all links on page
    return []


def extract_title_and_date_from_container(container: Tag) -> tuple[Optional[str], Optional[str], Optional[str]]:
    # Link
    link = container.find("a", href=True)
    url = link.get("href") if link else None

    # Title heuristic
    title = None
    for selector in ["h1", "h2", "h3", "h4", "[data-testid='card-headline']", ".title", ".headline"]:
        title_el = container.select_one(selector)
        title = safe_get_text(title_el)
        if title:
            break
    if not title and link:
        title = safe_get_text(link)

    # Date heuristic
    date = None
    time_el = container.find("time")
    if time_el:
        date = time_el.get("datetime") or safe_get_text(time_el)
    if not date:
        text = container.get_text(" ", strip=True)
        match = re.search(
            r"\b(\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|"
            r"[A-Z][a-z]+\s+\d{1,2},\s+\d{4})\b",
            text,
        )
        if match:
            date = match.group(1)

    return title, url, date


def extract_search_results(html: str, site: SiteConfig, query: str, search_url: str) -> list[SearchResult]:
    soup = BeautifulSoup(html, "html.parser")
    query_tokens = tokenize_query(query)

    results: list[SearchResult] = []
    seen_urls: set[str] = set()

    containers = find_candidate_link_containers(soup, site)
    if containers:
        for container in containers:
            title, raw_url, date = extract_title_and_date_from_container(container)
            if not raw_url:
                continue
            url = normalize_url(raw_url, f"https://{site.domain}")
            if url in seen_urls:
                continue
            if not domain_allowed(url, site) or url_blocked(url, site) or looks_like_asset(url):
                continue
            if not title:
                continue
            seen_urls.add(url)
            results.append(SearchResult(
                source=site.name,
                query=query,
                title=title,
                url=url,
                date_published=date,
                search_url=search_url
            ))

    # Fallback: collect raw links from page if structured containers were not enough
    if len(results) < 3:
        for a in soup.find_all("a", href=True):
            raw_url = a.get("href")
            if not raw_url:
                continue
            url = normalize_url(raw_url, f"https://{site.domain}")
            if url in seen_urls:
                continue
            if not domain_allowed(url, site) or url_blocked(url, site) or looks_like_asset(url):
                continue

            text = safe_get_text(a) or ""
            combined = f"{text} {url}".lower()

            # Some connection to query or article-like path
            query_hit = any(token in combined for token in query_tokens)
            path_hint_hit = any(hint.lower() in url.lower() for hint in site.article_path_hints)
            if not (query_hit or path_hint_hit):
                continue

            title = text if len(text) >= 8 else None
            if not title:
                # Use URL slug as weak fallback
                slug = urlparse(url).path.rstrip("/").split("/")[-1]
                slug = slug.replace("-", " ").replace("_", " ").strip()
                title = slug.title() if len(slug) >= 8 else None
            if not title:
                continue

            seen_urls.add(url)
            results.append(SearchResult(
                source=site.name,
                query=query,
                title=title,
                url=url,
                date_published=None,
                search_url=search_url
            ))

    return results


# =========================
# Article extraction
# =========================

def extract_article_metadata(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "title": extract_title_from_meta(soup),
        "date_published": extract_date_from_meta(soup),
        "author": extract_author_from_meta(soup),
        "summary": extract_summary_from_meta(soup),
        "article_text": None,
    }

    # JSON-LD can override/fill gaps
    for item in parse_json_ld(soup):
        item_type = item.get("@type")
        if isinstance(item_type, list):
            item_type_values = {str(x) for x in item_type}
        else:
            item_type_values = {str(item_type)} if item_type else set()

        if item_type_values.intersection({"NewsArticle", "Article", "ReportageNewsArticle", "AnalysisNewsArticle"}):
            data["title"] = data["title"] or item.get("headline")
            data["date_published"] = data["date_published"] or item.get("datePublished")
            data["author"] = data["author"] or extract_author(item.get("author"))
            data["summary"] = data["summary"] or item.get("description")

    data["article_text"] = extract_article_text(soup)
    return data


def enrich_result(result: SearchResult) -> Article:
    try:
        html = fetch_html(result.url)
        meta = extract_article_metadata(html, result.url)

        final_title = meta["title"] or result.title
        final_text = meta["article_text"]

        if not looks_like_article_page(result.url, final_title, final_text):
            return Article(
                source=result.source,
                query=result.query,
                title=final_title,
                url=result.url,
                date_published=meta["date_published"] or result.date_published,
                author=meta["author"],
                summary=meta["summary"],
                article_text=final_text,
                search_url=result.search_url,
                scraped_at=now_iso(),
                status="error",
                error="Fetched page does not look like a full article."
            )

        return Article(
            source=result.source,
            query=result.query,
            title=final_title,
            url=result.url,
            date_published=meta["date_published"] or result.date_published,
            author=meta["author"],
            summary=meta["summary"],
            article_text=final_text,
            search_url=result.search_url,
            scraped_at=now_iso(),
            status="ok"
        )
    except Exception as exc:
        return Article(
            source=result.source,
            query=result.query,
            title=result.title,
            url=result.url,
            date_published=result.date_published,
            search_url=result.search_url,
            scraped_at=now_iso(),
            status="error",
            error=str(exc)
        )


# =========================
# Search adapters
# =========================

def build_search_url(site: SiteConfig, query: str) -> Optional[str]:
    if not site.search_url_template:
        return None
    encoded = quote_plus(query)
    return site.search_url_template.format(query=encoded)


def search_site(site: SiteConfig, query: str, max_results: int = MAX_RESULTS_PER_SITE) -> list[SearchResult]:
    search_url = build_search_url(site, query)
    if not search_url:
        return []

    html = fetch_html(search_url)
    time.sleep(SLEEP_BETWEEN_REQUESTS)

    raw_results = extract_search_results(html, site, query, search_url)

    # sort loosely by whether a date exists and title length
    raw_results.sort(
        key=lambda r: (
            0 if r.date_published else 1,
            -len(r.title or "")
        )
    )

    return raw_results[:max_results]


def collect_articles(
    query: str,
    sites: Iterable[SiteConfig],
    max_results_per_site: int = MAX_RESULTS_PER_SITE
) -> list[Article]:
    articles: list[Article] = []

    for site in sites:
        print(f"\n=== Searching {site.name} ===")
        try:
            results = search_site(site, query, max_results=max_results_per_site)
            print(f"Found {len(results)} candidate links on {site.name}")

            for idx, result in enumerate(results, start=1):
                print(f"  [{idx}/{len(results)}] Fetching article: {result.url}")
                article = enrich_result(result)
                articles.append(article)
                time.sleep(SLEEP_BETWEEN_REQUESTS)

        except Exception as exc:
            print(f"Search failed for {site.name}: {exc}")
            articles.append(Article(
                source=site.name,
                query=query,
                title="",
                url="",
                search_url=build_search_url(site, query),
                scraped_at=now_iso(),
                status="error",
                error=f"Search failed: {exc}"
            ))

    return articles


# =========================
# Save output
# =========================

def save_as_json(articles: list[Article], output_file: str = OUTPUT_FILE) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([asdict(a) for a in articles], f, ensure_ascii=False, indent=2)


# =========================
# Main
# =========================

def main() -> None:
    articles = collect_articles(
        query=QUERY,
        sites=SITES,
        max_results_per_site=MAX_RESULTS_PER_SITE
    )
    save_as_json(articles, OUTPUT_FILE)

    ok_count = sum(1 for a in articles if a.status == "ok")
    err_count = sum(1 for a in articles if a.status == "error")

    print("\n=== Done ===")
    print(f"Saved {len(articles)} records to {OUTPUT_FILE}")
    print(f"OK: {ok_count} | Errors: {err_count}")


if __name__ == "__main__":
    main()