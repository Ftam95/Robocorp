
from selenium import webdriver 
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from urllib.parse import urlparse, unquote
from urllib.parse import urlparse, parse_qs
import requests
import time
import logging
import re, os
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

# Use the pre-installed ChromeDriver in the Docker image
service = Service(executable_path="/usr/bin/geckodriver")

driver = webdriver.Firefox(service=service, options=options)

logging.info("Started")

folder_Download = r"DownloadFolder"
if not os.path.exists(folder_Download):
    os.makedirs(folder_Download)
driver.get("https://www.latimes.com/")
driver.set_window_size(1920, 1080)  # Set a large window size

articles_data = []

wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-element='search-button']")))

def wait_for_element(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

search_button.click()

print("Clicked Search")
input_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-element='search-form-input']")))
input_element.send_keys("Artificial Intelligence"+Keys.ENTER)
print("Done")

# span_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Entertainment & Arts']")))
# checkbox = span_element.find_element(By.XPATH, "./preceding-sibling::input[@type='checkbox']")
# checkbox.click()

time.sleep(100)

articles = driver.find_elements(By.XPATH, "//ps-promo")
print(f"Found {len(articles)} articles.")
logging.info(f"Found {len(articles)} articles.")


# Define a function to check for money formats
def contains_money(text):
    return False

# Extract data for each article
for article in articles:
    # Extract title
    article_data = {}
    title_element = article.find_element(By.XPATH, ".//h3[@class='promo-title']/a")
    title = title_element.text.strip()
    article_data['Title'] = title
    print("Title:", title)
    
    # Extract date
    try:
        date_element = article.find_element(By.XPATH, ".//p[@class='promo-timestamp']")
        date = date_element.text.strip()
        print("Date Published:", date)
    
    except Exception as e:
        date = "Date Not Found"

    article_data['Date'] = date
    
    # Extract description (if available)
    try:
            description_element = wait_for_element(article, (By.XPATH, ".//p[contains(@class, 'promo-description')]"))
            description = description_element.text.strip()
    except Exception as e:
            description = "Description not available"

    article_data['Description'] = description

    # Get the description
    try:
        picture_element = article.find_element(By.XPATH, ".//img[@class='image']")
        #description = picture_element.get_attribute("alt")
        picture_description = picture_element.get_attribute("alt")
        picture_src = picture_element.get_attribute("src")
        print("Picture SRC:", picture_src)
        print("Picture description:>>>>>> ",picture_description)
        article_data['File Name Description'] = picture_description
        parsed_url = urlparse(picture_src)

        picture_filename_download = parsed_url.path.split("/")[-1]
        
        try:
            print("tryyyyyy>>>>>>>>>>>>>>>>>")
            response = requests.get(picture_src)
            print(">>>>>>>>>>>> Response is >>>>>>>>>>>>>>"+str(response.status_code))
            print("Try to download image")
# Check if the request was successful
             
            query_params = parse_qs(parsed_url.query)

            if 'url' in query_params:
                picture_url = query_params['url'][0]
                print("Extracted Picture URL:", picture_url)

                parsed_picture_url = urlparse(picture_url)
                path = parsed_picture_url.path
                match = re.search(r'/([^/]+\.(?:jpg|jpeg|png|gif))$', path)
    
                if match:
                    picture_filename = match.group(1)
                    if response.status_code == 200:
                        print("Status code <><<><<><><><><><><><><><>>>>>>>>>>>>>>>>>>>> shld download" )
    # Save the image to a fileopen(picture_filename, "wb") as file:
                        output_file_path = os.path.join(folder_Download, picture_filename)
                        with open(output_file_path, "wb") as file:
                            file.write(response.content)
                        print("Image downloaded successfully as:", output_file_path)
                    else:
                        print("Failed to download image." +str(response.status_code))
       
                else:
                    picture_filename = "Filename not found"
            else:
                picture_filename = "URL parameter 'url' not found"
            

            article_data['File Name'] = picture_filename

            print("Picture filename::: ", picture_filename)
            print("Picture Description:", picture_description)
        except Exception as e:
            print("Error is >>>>>>> {}".format(e))
    except Exception as e:
        picture_description = "Picture not available"    
    

    articles_data.append(article_data)


df = pd.DataFrame(articles_data)

# Write DataFrame to an Excel file
excel_file = "articles_data.xlsx"
df.to_excel(excel_file, index=False)

        

# Parse the URL


# Get the filename from the path


    # Get the picture URL
    # picture_url = picture_element.get_attribute("src")

    # print("Picture Description:", picture_description)
    # print("Picture URL:", picture_url)
    
    # Log the extracted data
    # print("Title:", title)
    # print("Date Published:", date)
    # print("Description:", description)
    #print("Picture URL:", picture_url)    


# Close the browser
#driver.quit()
