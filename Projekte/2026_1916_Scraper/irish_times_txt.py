from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.irishtimes.com"

# Setup headless Chrome
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Load the search page
driver.get("https://www.irishtimes.com/search/?query=Easter+Rising")
time.sleep(3)  # wait for JavaScript to load content

# Parse page HTML with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Find all headline divs
headline_divs = soup.find_all("div", class_="queryly_item_title")

# Save headline, URL, and date to a text file
with open("easter_rising_headlines.txt", "w", encoding="utf-8") as f:
    for div in headline_divs:
        headline = div.get_text(strip=True)
        parent_link = div.find_parent("a")
        url = parent_link["href"] if parent_link else None
        if url and url.startswith("/"):
            url = BASE_URL + url
        elif not url:
            url = "No URL"

        # Get the publication date (next sibling div with the date style)
        date_div = div.find_next("div", style="margin-top:6px;color:#555;font-size:12px;")
        pub_date = date_div.get_text(strip=True) if date_div else "No date"

        f.write(f"{headline}\n{url}\n{pub_date}\n\n")

print(f"{len(headline_divs)} headlines with URLs and dates saved to easter_rising_headlines.txt")

driver.quit()
