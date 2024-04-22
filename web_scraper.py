from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests
import re
import os
from urllib.parse import urlparse, parse_qs
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys


def wait_for_element(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def count_occurrences(string, search_phrase):
    return string.lower().count(search_phrase.lower())

def contains_money(string):
    money_formats = [
        r"\$\d+(\.\d{1,2})?",  # $11.1 or $111,111.11
        r"\d+ dollars",  # 11 dollars
        r"\d+ USD"  # 11 USD
    ]
    
    for money_format in money_formats:
        if re.search(money_format, string, re.IGNORECASE):
            return True
    return False

def scrape_articles(driver, search_phrase, folder_Download):
    articles_data = []

    search_button = wait_for_element(driver, (By.CSS_SELECTOR, "button[data-element='search-button']"))
    search_button.click()

    input_element = wait_for_element(driver, (By.CSS_SELECTOR, "input[data-element='search-form-input']"))
    input_element.send_keys(search_phrase + Keys.ENTER)

    newest_option = (driver.find_element(By.XPATH, "//option[@value='1']"))  # Assuming '1' is for "Newest"
#   newest_option.click()

    time.sleep(10)

    articles = driver.find_elements(By.XPATH, "//ps-promo")

    for article in articles:
        article_data = {}

        title_element = article.find_element(By.XPATH, ".//h3[@class='promo-title']/a")
        title = title_element.text.strip()
        article_data['Title'] = title

        try:
            date_element = article.find_element(By.XPATH, ".//p[@class='promo-timestamp']")
            date = date_element.text.strip()
        except Exception as e:
            date = "Date Not Found"

        article_data['Date'] = date

        try:
            description_element = wait_for_element(article, (By.XPATH, ".//p[contains(@class, 'promo-description')]"))
            description = description_element.text.strip()
        except Exception as e:
            description = "Description not available"

        article_data['Description'] = description

        try:
            count = count_occurrences(title, search_phrase) + count_occurrences(description, search_phrase)
        except Exception as e:
            count = 0
        article_data['Search Phrase Count'] = count   

        try:
            contains_money_flag = contains_money(title) or contains_money(description)
        except Exception as e:
            contains_money_flag = False
        article_data['Contains Money'] = contains_money_flag

        # Download image and retrieve file name
        try:
            picture_element = article.find_element(By.XPATH, ".//img[@class='image']")
            picture_description = picture_element.get_attribute("alt")
            picture_src = picture_element.get_attribute("src")

            response = requests.get(picture_src)
            if response.status_code == 200:
                parsed_url = urlparse(picture_src)
                picture_filename_download = parsed_url.path.split("/")[-1]
                
                query_params = parse_qs(parsed_url.query)

                if 'url' in query_params:
                    picture_url = query_params['url'][0]
                    parsed_picture_url = urlparse(picture_url)
                    path = parsed_picture_url.path
                    match = re.search(r'/([^/]+\.(?:jpg|jpeg|png|gif))$', path)
        
                    if match:
                        picture_filename = match.group(1)
                        output_file_path = os.path.join(folder_Download, picture_filename)
                        with open(output_file_path, "wb") as file:
                            file.write(response.content)
                    else:
                        picture_filename = "Filename not found"
                else:
                    picture_filename = "URL parameter 'url' not found"

                article_data['File Name'] = picture_filename
                article_data['File Name Description'] = picture_description

            else:
                picture_filename = "Failed to download image."
                article_data['File Name'] = picture_filename
        except Exception as e:
            picture_description = "Picture not available" 
            article_data['File Name Description'] = picture_description

        articles_data.append(article_data)

    return articles_data

