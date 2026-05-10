from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import time
from urllib.parse import urlencode

BASE_URL = "https://www.anphoblacht.com"
QUERY = "Easter Rising"
SOURCE = "An Phoblacht"

# Note:
# This script only scrapes the first page!


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_search_url():
    """
    Baut die Such-URL dynamisch.
    Enddatum = heutiges Datum + 1 Tag
    """
    start_date = "01/01/2026"
    end_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    params = {
        "words": "all",
        "words_include": QUERY,
        "words_exclude": "",
        "dates": "choose",
        "date_start": start_date,
        "date_end": end_date,
    }

    return f"{BASE_URL}/search/results?{urlencode(params)}"


def extract_article_text(driver, url):
    """
    Lädt eine Artikelseite und versucht, den Fließtext zu extrahieren.
    Gibt (article_text, status, error) zurück.
    """
    try:
        driver.get(url)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Erst versuchen: article-Tag
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
            text = "\n".join(
                p.get_text(" ", strip=True)
                for p in paragraphs
                if p.get_text(strip=True)
            )
            if len(text.strip()) > 200:
                return text.strip(), "ok", None

        # Fallback: main-Tag
        main = soup.find("main")
        if main:
            paragraphs = main.find_all("p")
            text = "\n".join(
                p.get_text(" ", strip=True)
                for p in paragraphs
                if p.get_text(strip=True)
            )
            if len(text.strip()) > 200:
                return text.strip(), "ok", None

        # Letzter Fallback: alle Absätze
        paragraphs = soup.find_all("p")
        text = "\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )
        if len(text.strip()) > 200:
            return text.strip(), "ok", None

        return None, "error", "Fetched page does not look like a full article."

    except Exception as e:
        return None, "error", str(e)


# Setup headless Chrome
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

results = []
SEARCH_URL = get_search_url()

try:
    # Load the search page
    driver.get(SEARCH_URL)
    time.sleep(3)

    # Parse page HTML with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Mögliche Suchergebnis-Links sammeln
    # Falls die Struktur leicht variiert, ist diese Variante robuster als eine einzelne Klasse
    result_links = soup.find_all("a", href=True)

    seen_urls = set()

    for link in result_links:
        href = link.get("href")
        title = link.get_text(strip=True)

        if not href or not title:
            continue

        # Nur interne Links
        if href.startswith("/"):
            url = BASE_URL + href
        elif href.startswith(BASE_URL):
            url = href
        else:
            continue

        # Nur echte Artikel unter /contents/
        if "/contents/" not in url:
            continue

        # Doppelte vermeiden
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Titel zu kurz => wahrscheinlich kein echter Treffer
        if len(title) < 5:
            continue

        # Veröffentlichungsdatum versuchen zu finden:
        # Häufig steht es in der Umgebung des Links
        pub_date = None
        parent = link.find_parent()
        if parent:
            time_tag = parent.find("time")
            if time_tag:
                pub_date = time_tag.get("datetime") or time_tag.get_text(strip=True)

        article_text = None
        status = "ok"
        error = None

        article_text, status, error = extract_article_text(driver, url)

        result = {
            "source": SOURCE,
            "query": QUERY,
            "title": title,
            "url": url,
            "date_published": pub_date,
            "article_text": article_text,
            "search_url": SEARCH_URL,
            "date_scraped": now_iso(),
            "status": status,
            "error": error
        }

        results.append(result)

    # Save JSON
    with open("easter_rising_an_phoblacht.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"{len(results)} results saved to easter_rising_an_phoblacht.json")

finally:
    driver.quit()