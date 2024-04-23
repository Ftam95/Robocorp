from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
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
import re, os, json
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from robocorp.tasks import task
from robocorp import workitems
from config_reader import read_config
from web_scraper import scrape_articles
from robocorp  import workitems


@task
def otomatika():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

#     # # # # Use the pre-installed ChromeDriver in the Docker image
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    # service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)

    logging.info("Started")

    workitem = workitems.inputs.current

    # Use the work item in the current task
    config_data = workitem['payload']['input']
    search_phrase = config_data['search_phrase']
    news_category = config_data['news_category']
    number_of_months = config_data['number_of_months']

    print("search phrase is >>>>>>>"+search_phrase)


    folder_Download = r"output"
    if not os.path.exists(folder_Download):
        os.makedirs(folder_Download)

    driver.get("https://www.latimes.com/")
    driver.set_window_size(1920, 1080)

    # config_data = read_config('config.json')
    # search_phrase = config_data['search_phrase']
    # news_category = config_data['news_category']
    # number_of_months = config_data['number_of_months']

    articles_data = scrape_articles(driver, search_phrase, folder_Download)

    df = pd.DataFrame(articles_data)
    excel_file = os.path.join(folder_Download, search_phrase+".xlsx")
    df.to_excel(excel_file, index=False)

    driver.quit()
