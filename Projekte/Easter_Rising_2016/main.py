import requests
import csv
import time
import random
from waybackpy import WaybackMachineCDXServerAPI
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, Timeout

# List of news sites to check
news_sites = [
   # "https://www.rte.ie/news/",
   # "https://www.irishtimes.com/",
   # "https://www.independent.ie/",
   # "https://www.thejournal.ie/",
   # "https://www.bbc.com/news/world-europe-26565457",
   "https://www.anphoblacht.com/"
]

# Search parameters
start_date = 20160101  # Start of 2016
end_date = 20160130  # End of 2016
keyword = "1916 Easter Rising"

# Output CSV file
csv_filename = "wayback_1916_easter_rising_results.csv"


def fetch_snapshots(site, retries=5, delay=3):
    """Fetch archived snapshots with retries and exponential backoff."""
    attempt = 0
    while attempt < retries:
        try:
            wayback = WaybackMachineCDXServerAPI(site, start_timestamp=start_date, end_timestamp=end_date)
            return list(wayback.snapshots())  # Ensure it's a list
        except ConnectionError:
            wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Connection error. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            attempt += 1
        except Timeout:
            print("Request timed out. Skipping site.")
            return []
    print("Max retries reached. Skipping site.")
    return []


# Open CSV file to store results
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Website", "Archived URL", "Date Found"])

    for site in news_sites:
        print(f"Searching archives for {site}...")
        snapshots = fetch_snapshots(site)

        for snapshot in snapshots:
            archived_url = snapshot.archive_url  # Corrected attribute
            timestamp = snapshot.timestamp  # Use as string, not method
            print(f"Found: {archived_url} ({timestamp})")
            writer.writerow([site, archived_url, timestamp])
            time.sleep(random.uniform(1, 3))  # Random delay to prevent rate limiting
