GOALS AND BASICS


The goal of this little Python program is to make it faster to search through the collection of letters about the 1916 Easter Rising in Dublin, collected in the citizens science project “Letters 1916-1923.” For this goal, it is using the Selenium library, which simulates a human’s interaction with any given website. It can for example click on links and boxes on the site or write into a search bar. In a last step, the titles of and links to the letters found in the search are getting written into a CSV-file. This makes possible searching for a number of keywords automatically without having to copy every link by hand and provides a file with which one can work further.
The most important part of the code for any user is the keyword. In this case it is set to “Casement,” referring to Roger Casement, who trying to garner German support for Irish independence and was later hanged by the brits. But the keyword can be freely set to anything one likes, from a single letter to a whole sentence. Just remember that you are basically typing into a search-bar on a website. So try using keywords you would use in such a scenario too.
Note: The name of the CSV-file will always include the keyword so to make simpler identifying the results of different searches at a later point.
```
keyword = "Casement"
csv_name = f"letters1916_{keyword}_results.csv"
```

PROBLEMS AND DEFINITONS


For the code to work, several problems have to be solved: the website has to be opened, the keyword has to be searched for, it has to be established how many results were found, the results have to be extracted, the website has to be closed. Let’s have a look at how to program does this.

Opening the website

  To open the website, we have to first open the browser, then open the website in it. Selenium provides a simple solution for this, which is defined as “setup” following Selenium convention.
  ```
  def setup()
      driver = webdriver.Chrome()
      driver.get("https://letters1916.ie/")
      return driver
  ```

Searching for the keyword

  To search for the keyword, we define a function “search_keyword,” which gets the website, finds the search-bar on the website and types the keyword into it. As a last step, it has to return the new URL (which will look something like this https://letters1916.ie/fullsearch/casement) as the new starting point for our actions.
  ```
  def search_keyword(keyword):
    driver = setup()
    search_bar = driver.find_element(By.NAME, "search-bar")
    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.ENTER)
    driver.get(driver.current_url)
    return driver
  ```

Establishing number of results

  The website shows two things interesting to us in this step: 1. How many letters were found and 2. on how many pages they are displayed.
  To extract 1. we just need to find the element that includes the text for this information and extract it. If there is no result found, we have to expect a NoSuchElementError and display a message that there are no results for this keyword instead.
  ```
  try:
    print(f"Number of letters found for keyword(s) {keyword}: {driver.find_element(By.CLASS_NAME, "results-found").text}.")
  except NoSuchElementException:
    print(f"No letters found for the keyword(s): {keyword}.")
  ```
  To extract 2. we need to find the field where users can type in a page in the format of “x /number of pages found,” e.g. 1 /16. When extracting the page number, we will get a list of elements of which the first two are a space (“”) and the slash (“/”). The remaining third (and maybe forth or fifth) element constitutes the page number, meaning we have to multiply the numbers according to the length of the list.
  Establishing the number of pages is important later on in the code, when trying to determine when the last page with results has been extracted.
  ```
  found_pages = list(driver.find_element(By.CLASS_NAME, "input-group-addon").text)
  if len(found_pages) == 3:
      number_of_pages = int(found_pages[2])
  elif len(found_pages) == 4:
      number_of_pages = int(found_pages[2]) * 10 + int(found_pages[3])
  elif len(found_pages) == 5:
      number_of_pages = int(found_pages[2]) * 100 + int(found_pages[3])*10 + int(found_pages[4])
  print(f"Number of Pages found: {number_of_pages}")
  ```

Extracting the results

  This is the main challenge of the task and can be further split into different tasks. First, we need to find a way to extract the letters and their URLs from the site. Secondly, we need a way to turn to the next page of results. This is necessary because the site only displays ten letters at a time. Then we need to repeat this process until we have reached the last page and extracted all the letters. Lastly, we need to save the results in the CSV-file.
  1. Extracting the letters: To extract the letters, we define a function “get_letters.” This function first waits for three seconds to let all website elements load. Then it finds all the titles of the letters (coded as h4-elements on the website) and puts them in a list. It then extracts the pure text of the letter name (a-element) and the link to the letter (href-element) for each list element. Afterwards it appends links and names to two separate lists so that the number of the list element for the name and the link are the same. This way we create a way to connect both elements to each other later. 
```
    def get_letters():
        time.sleep(3)
        letters = driver.find_element(By.CLASS_NAME, "search-letters-container")
        letter_names = letters.find_elements(By.CSS_SELECTOR, "h4")
        for name in letter_names:
            titel = name.find_element(By.CSS_SELECTOR, "a")
            link = titel.get_attribute("href")
            all_links.append(link)
            all_titles.append(titel.text)
```
  2.	Turning the page: To turn the page we define a function “turn_page.” This function finds the list of elements making up the page-browser element on the website (boxes with the numbers 1 through 10). For every element in this list, the function then checks if it is the same as the current page number (which is defined as 1 at the start of the code) + 1. It then clicks on this element. Outside the defined function, one is then added to the page number, so when recalling the function page number + 1 now equals 3 and so on.
```
    def turn_page(): # Turns the page of the "Letter"-body on the website
        letters = driver.find_element(By.CLASS_NAME, "search-letters-container")
        page_browser = letters.find_element(By.CLASS_NAME, "pagination-container")
        pages = page_browser.find_elements(By.CSS_SELECTOR, "li")
        for page in pages:
            if page.text == str(page_number+1):
                print(f"Page {page.text} found.")
                page.find_element(By.CSS_SELECTOR, "span").click()
                print(f"Turning to page number {page_number + 1}.")
```
   But we are not done yet. The reason for this is, that the website throws a curve ball at us, when we enter page three. When clicking on page three, the page-browser element on the website reloads and now only has 8 elements in it instead of 10. This leads to the “turn_page” function producing an error. This is why another function “turn_page_three_to_four” is defined. It does the same thing as “turn_page” but breaks when calling for the elements 8, 9, and 10 of the page-browser, which do not exist anymore. This prevents the error and lets the code run as planned.
```
    def turn_page_three_to_four():
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
```
  3.	Saving the results: Saving the results is done by writing into a CSV-file using the CSV-library. The structure of the resulting file is as follows: There is a first line giving information about the website and keyword used. After this there is an empty line and a line with the headings (Letter Name and Link). Under these headings the extracted names and links are written respectively, by always writing the same list element number of both the “all_names”-list and the “all_links”-list into the same row.
```
    with open(csv_name, mode="w", newline="", encoding="utf-8") as f:
            list_tracker = 0
            writer = csv.writer(f)
            writer.writerow([f"Letters on letter1916.ie for the keyword: {keyword}"])
            writer.writerow([""])
            writer.writerow(["Letter Name", "Link"])
            for link in all_links:
                writer.writerow([all_titles[0 + list_tracker], link])
                list_tracker += 1
```
    
Closing the website

  To close the website, Selenium provides for a simple function, which is defined as “teardown(driver)” following the convention of Selenium usage.
  ```
def teardown(driver):
    driver.quit()
```

STRUCTURE OF THE FINAL CODE

The final code is structured in five parts mirroring the structure of the PROBLEMS and BASICS part of this documentation.  The only thing to add here is about part three, the extracting of the letters and the turning of the pages. Especially interesting here is, how the code knows it reached the last page and can start saving the results.
Because we need to use a different function for page 3 than for all other pages, the first two pages are extracted and turned by their own blocks of code, before page 3 is extracted and then turned by the special function “turn_page_three_to _four.” All following pages are extracted and turned in a while-loop. The loop’s condition is set to true by default and changes to false as soon as the number of the page it would need to turn to (page_number) exceedes the number of pages actually found when solving problem 2 (number_of_pages).
After the condition becomes false, the program goes on two compile the CSV-file and close the website.
