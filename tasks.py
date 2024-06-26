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
from driver import drivers


@task
def otomatika():
    
    driver= drivers()
    
    logging.info("Started")

    workitem = workitems.inputs.current

    search_phrase =workitem.payload['search_phrase']
    number_of_days = workitem.payload['number_of_days']
    

    # config_data = read_config('config.json')
    # search_phrase = config_data['search_phrase']
    # news_category = config_data['news_category']
    # number_of_days = config_data['number_of_days']


    folder_Download = r"output"
    if not os.path.exists(folder_Download):
        os.makedirs(folder_Download)

    driver.get("https://www.latimes.com/")
    driver.set_window_size(1920, 1080)

    articles_data = scrape_articles(driver, search_phrase, folder_Download)

    df = pd.DataFrame(articles_data)
    excel_file = os.path.join(folder_Download, search_phrase+".xlsx")
    df.to_excel(excel_file, index=False)

    driver.quit()
