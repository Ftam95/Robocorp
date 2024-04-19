from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import requests
import time
import logging
import re, os, json
import pandas as pd
from selenium.webdriver.chrome.options import Options

class LaTimes:
    def __init__(self, config_file_path='config.json'):
        self.config_data = self.read_config(config_file_path)
        self.search_phrase = self.config_data['search_phrase']
        self.number_of_months = self.config_data['number_of_months']
        self.articles_data = []

        # Setting up the Selenium WebDriver

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")

        # # Use the pre-installed ChromeDriver in the Docker image
        service = Service(executable_path="/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)
        # self.service = Service(executable_path="chromedriver.exe")
        # self.driver = webdriver.Chrome(service=self.service)
        self.wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds

    def read_config(self, configfile):
        with open(configfile, 'r') as config_file:
            data = json.load(config_file)
        return data

    def count_occurrences(self, string, search_phrase):
        return string.lower().count(search_phrase.lower())

    def contains_money(self, string):
        # Define possible formats for money
        money_formats = [
            r"\$\d+(\.\d{1,2})?",  # $11.1 or $111,111.11
            r"\d+ dollars",         # 11 dollars
            r"\d+ USD"              # 11 USD
        ]
        
        # Check if the string contains any of the money formats
        for money_format in money_formats:
            if re.search(money_format, string, re.IGNORECASE):
                return True
        return False

    def scrape(self):
        logging.info("Started")
        folder_Download = r"output"
        if not os.path.exists(folder_Download):
            os.makedirs(folder_Download)
        
        self.driver.get("https://www.latimes.com/")
        self.driver.set_window_size(1920, 1080)

        search_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-element='search-button']")))
        search_button.click()

        input_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-element='search-form-input']")))
        input_element.send_keys(self.search_phrase+Keys.ENTER)

        select_element = self.driver.find_element(By.CLASS_NAME, "select-input")
        select_element.click()

        newest_option = self.driver.find_element(By.XPATH, "//option[@value='1']")  # Assuming '1' is for "Newest"
        newest_option.click()

        time.sleep(10)

        articles = self.driver.find_elements(By.XPATH, "//ps-promo")
        print(f"Found {len(articles)} articles.")
        logging.info(f"Found {len(articles)} articles.")

        # Extract data for each article
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
                description_element = article.find_element(By.XPATH, ".//p[contains(@class, 'promo-description')]")
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
                
                try:
                    response = requests.get(picture_src)
                    query_params = parse_qs(parsed_url.query)

                    if 'url' in query_params:
                        picture_url = query_params['url'][0]
                        parsed_picture_url = urlparse(picture_url)
                        path = parsed_picture_url.path
                        match = re.search(r'/([^/]+\.(?:jpg|jpeg|png|gif))$', path)
        
                        if match:
                            picture_filename = match.group(1)
                            if response.status_code == 200:
                                output_file_path = os.path.join(folder_Download, picture_filename)
                                with open(output_file_path, "wb") as file:
                                    file.write(response.content)
                            else:
                                print("Failed to download image." + str(response.status_code))
                        else:
                            picture_filename = "Filename not found"
                    else:
                        picture_filename = "URL parameter 'url' not found"
                    
                    article_data['File Name'] = picture_filename
                except Exception as e:
                    print("Error: {}".format(e))
            except Exception as e:
                picture_description = "Picture not available"    
            
            self.articles_data.append(article_data)

        df = pd.DataFrame(self.articles_data)
        excel_file = os.path.join(folder_Download, self.search_phrase+".xlsx")
        df.to_excel(excel_file, index=False)

        self.driver.quit()

# Example usage:
scraper = LaTimes()
scraper.scrape()
