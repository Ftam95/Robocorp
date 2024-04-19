import os
import json
import re
import requests
import logging
import time
import pandas as pd
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class LatimesArticleScraper:
    def __init__(self, config_file='config.json'):
        self.config_data = self.read_config(config_file)
        self.search_phrase = self.config_data['search_phrase']
        self.folder_download = "output"
        self.setup_logging()
        self.setup_driver()

    def read_config(self, config_file):
        with open(config_file, 'r') as config_file:
            data = json.load(config_file)
        return data

    def setup_logging(self):
        if not os.path.exists(self.folder_download):
            os.makedirs(self.folder_download)
        logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")

        service = Service(executable_path="/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)

        #Runnin glocal
        #service = Service(executable_path="chromedriver.exe")
        #self.driver = webdriver.Chrome(service=service)
        self.driver.set_window_size(1920, 1080)
        

    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def count_occurrences(self, string, search_phrase):
        return string.lower().count(search_phrase.lower())

    def contains_money(self, string):
        # Define possible formats for money
        money_formats = [
            r"\$\d+(\.\d{1,2})?",  # $11.1
            r"\d+ dollars",         # 11 dollars
            r"\d+ USD"              # 11 USD
        ]
        
        # Check if the string contains any of the money formats
        for money_format in money_formats:
            if re.search(money_format, string, re.IGNORECASE):
                return True
        return False

    def scrape_articles(self):
        self.driver.get("https://www.latimes.com/")
        search_button = self.wait_for_element((By.CSS_SELECTOR, "button[data-element='search-button']"))
        search_button.click()

        input_element = self.wait_for_element((By.CSS_SELECTOR, "input[data-element='search-form-input']"))
        input_element.send_keys(self.search_phrase + Keys.ENTER)

        select_element = self.driver.find_element(By.CLASS_NAME, "select-input")
        select_element.click()

        newest_option = self.driver.find_element(By.XPATH, "//option[@value='1']")  # Optioon 1 is the Newest. Option 0 relevance
        newest_option.click()

        time.sleep(10)

        articles = self.driver.find_elements(By.XPATH, "//ps-promo")
        logging.info(f"Found {len(articles)} articles.")

        articles_data = []
        for article in articles:
            article_data = {}
            #Get Title
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
                description_element = self.wait_for_element((By.XPATH, ".//p[contains(@class, 'promo-description')]"))
                description = description_element.text.strip()
            except Exception as e:
                description = "Description not available"
            article_data['Description'] = description

            count = self.count_occurrences(title, self.search_phrase) + self.count_occurrences(description, self.search_phrase)
            article_data['Search Phrase Count'] = count   

            contains_money_flag = self.contains_money(title) or self.contains_money(description)
            article_data['Contains Money'] = contains_money_flag

            try:
                picture_element = article.find_element(By.XPATH, ".//img[@class='image']")
                picture_description = picture_element.get_attribute("alt")
                picture_src = picture_element.get_attribute("src")
                article_data['File Name Description'] = picture_description

                parsed_url = urlparse(picture_src)
                picture_filename_download = parsed_url.path.split("/")[-1]
                
                response = requests.get(picture_src)
                if response.status_code == 200:
                    query_params = parse_qs(parsed_url.query)
                    if 'url' in query_params:
                        picture_url = query_params['url'][0]
                        parsed_picture_url = urlparse(picture_url)
                        path = parsed_picture_url.path
                        match = re.search(r'/([^/]+\.(?:jpg|jpeg|png|gif))$', path)
                        if match:
                            picture_filename = match.group(1)
                            output_file_path = os.path.join(self.folder_download, picture_filename)
                            with open(output_file_path, "wb") as file:
                                file.write(response.content)
                            article_data['File Name'] = picture_filename
                        else:
                            picture_filename = "Filename not found"
                    else:
                        picture_filename = "URL parameter 'url' not found"
                else:
                    picture_filename = "Failed to download image." + str(response.status_code)
                article_data['File Name'] = picture_filename
            except Exception as e:
                logging.error(f"Error processing article: {e}")

            articles_data.append(article_data)

        df = pd.DataFrame(articles_data)
        excel_file = os.path.join(self.folder_download, self.search_phrase + ".xlsx")
        df.to_excel(excel_file, index=False)

    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = LatimesArticleScraper()
    try:
        scraper.scrape_articles()
    finally:
        scraper.close_driver()
