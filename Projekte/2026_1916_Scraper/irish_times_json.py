from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import time

BASE_URL = "https://www.irishtimes.com"
SEARCH_URL = "https://www.irishtimes.com/search/?query=Easter+Rising"
QUERY = "Easter Rising"
SOURCE = "Irish Times"

#Note:
#This script only scrapes the first page!

def now_iso():
    return datetime.now(timezone.utc).isoformat()


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
            text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True))
            if len(text.strip()) > 200:
                return text.strip(), "ok", None

        # Fallback: main-Tag
        main = soup.find("main")
        if main:
            paragraphs = main.find_all("p")
            text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True))
            if len(text.strip()) > 200:
                return text.strip(), "ok", None

        # Letzter Fallback: alle Absätze
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True))
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

try:
    # Load the search page
    driver.get(SEARCH_URL)
    time.sleep(3)

    # Parse page HTML with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Find all headline divs
    headline_divs = soup.find_all("div", class_="queryly_item_title")

    for div in headline_divs:
        headline = div.get_text(strip=True)

        parent_link = div.find_parent("a")
        url = parent_link["href"] if parent_link else None

        if url and url.startswith("/"):
            url = BASE_URL + url
        elif not url:
            url = None

        # publication date
        date_div = div.find_next("div", style="margin-top:6px;color:#555;font-size:12px;")
        pub_date = date_div.get_text(strip=True) if date_div else None

        article_text = None
        status = "ok"
        error = None

        if url:
            article_text, status, error = extract_article_text(driver, url)
        else:
            status = "error"
            error = "No URL found for search result."

        result = {
            "source": SOURCE,
            "query": QUERY,
            "title": headline,
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
    with open("easter_rising_irish_times.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"{len(results)} results saved to easter_rising_irish_times.json")

finally:
    driver.quit()