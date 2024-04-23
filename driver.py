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


def drivers():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    ## running on lcal
    # service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)

    return driver