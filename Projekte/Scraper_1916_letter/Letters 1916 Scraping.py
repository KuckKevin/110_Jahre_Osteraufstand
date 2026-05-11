import csv
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time

keyword = "Casement" # The keyword is changable to whatever you want
csv_name = f"letters1916_{keyword}_results.csv" # Note that the keyword is part of the file name
all_links = []
all_titles = []
page_number = 1

def setup():
    driver = webdriver.Chrome()
    driver.get("https://letters1916.ie/")
    return driver
def teardown(driver):
    driver.quit()
def search_keyword(keyword): # Searches for a Keyword and returns URL of the search
    driver = setup()
    search_bar = driver.find_element(By.NAME, "search-bar")
    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.ENTER)
    driver.get(driver.current_url)
    return driver
def get_letters(): # Finds the letter titels and the links to the letters and puts them in separat list
    time.sleep(3) #(Needs to be here to prevent loading errors)
    letters = driver.find_element(By.CLASS_NAME, "search-letters-container")
    letter_names = letters.find_elements(By.CSS_SELECTOR, "h4")
    for name in letter_names:
        titel = name.find_element(By.CSS_SELECTOR, "a")
        link = titel.get_attribute("href")
        all_links.append(link)
        all_titles.append(titel.text)
def turn_page(): # Turns the page of the "Letter"-body on the website
    letters = driver.find_element(By.CLASS_NAME, "search-letters-container")
    page_browser = letters.find_element(By.CLASS_NAME, "pagination-container")
    pages = page_browser.find_elements(By.CSS_SELECTOR, "li")
    for page in pages:
        if page.text == str(page_number+1):
            print(f"Page {page.text} found.")
            page.find_element(By.CSS_SELECTOR, "span").click()
            print(f"Turning to page number {page_number + 1}.")
def turn_page_three_to_four(): # This is necessary because the page-browser shortens on when page 4 is loaded from 10 to 8 units.
    letters = driver.find_element(By.CLASS_NAME, "search-letters-container")
    page_browser = letters.find_element(By.CLASS_NAME, "pagination-container")
    pages = page_browser.find_elements(By.CSS_SELECTOR, "li")
    for page in pages:
        if page.text == "8":
            break
        elif page.text == "9":
            break
        elif page.text == "10":
            break
        elif page.text == str(page_number + 1):
            page.find_element(By.CSS_SELECTOR, "span").click()
            print(f"Turning to page number {page_number + 1}.")

# 1. Search for the keyword on the letters1916-Website and wait for everything to load.
driver = search_keyword(keyword)
time.sleep(3)

# 2. Establish the number of pages and letter found.
found_pages = list(driver.find_element(By.CLASS_NAME, "input-group-addon").text)
if len(found_pages) == 3:
    number_of_pages = int(found_pages[2])
elif len(found_pages) == 4:
    number_of_pages = int(found_pages[2]) * 10 + int(found_pages[3])
elif len(found_pages) == 5:
    number_of_pages = int(found_pages[2]) * 100 + int(found_pages[3])*10 + int(found_pages[4])
print(f"Number of Pages found: {number_of_pages}")
try:
    print(f"Number of letters found for keyword(s) {keyword}: {driver.find_element(By.CLASS_NAME, "results-found").text}.")
except NoSuchElementException:
    print(f"No letters found for the keyword(s): {keyword}.")

# 3. Find all URLs of the displayed letters and puts Titel of the letter and link in separate lists then turns page.
# Page 1
get_letters()
print("Successfully extracted letters.")
turn_page()
page_number += 1
# Page 2
get_letters()
print("Successfully extracted letters.")
turn_page()
page_number += 1
# Page 3
get_letters()
print("Successfully extracted letters.")
turn_page_three_to_four()
page_number += 1
# All following pages
condition = True
while condition == True: # Creates a loop that lasts till the page number is higher than the number of pages (= all letters extracted).
    get_letters()
    print(f"Successfully extracted letters on {page_number}.")
    turn_page()
    page_number += 1
    if page_number > number_of_pages:
        condition = False

# 4. When all letters extracted are extracted: Writes all links and corresponding titels into a CSV-document.
else:
    with open(csv_name, mode="w", newline="", encoding="utf-8") as f:
        list_tracker = 0
        writer = csv.writer(f)
        writer.writerow([f"Letters on letter1916.ie for the keyword: {keyword}"])
        writer.writerow([""])
        writer.writerow(["Letter Name", "Link"])
        for link in all_links:
            writer.writerow([all_titles[0 + list_tracker], link])
            list_tracker += 1

# 5. Closes the driver.
teardown(driver)
