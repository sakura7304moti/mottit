from io import StringIO, BytesIO
import os
import re
from time import sleep
import random
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import datetime
import pandas as pd
import platform
from selenium.webdriver.common.keys import Keys

# import pathlib
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib

from .const import get_cookie

def init_driver(headless=True):#get chrome driver
    options = ChromeOptions()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # An error will occur without this line
        options.add_argument('--window-size=900,1000')
        options.add_experimental_option('prefs', "'profile.default_content_setting_values.notifications': 2")
        options.headless = True
    else:
        options.headless = False
    try:
        driver_path = chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options, executable_path=driver_path)
    except Exception as e:
        print(e)
        driver = webdriver.Chrome(options=options)
    driver.get("https://www.reddit.com/")
    cookie = get_cookie()
    for c in cookie:
        driver.add_cookie(c)
    driver.get("https://www.reddit.com/")
    driver.set_page_load_timeout(100)
    sleep(3)
    driver.get("https://www.reddit.com/")
    return driver

def page_url(first_name:str,last_name:str=None):#searched page url
    base_url='https://www.reddit.com/r/Hololewd/new'
    if last_name == None:#fullName only?
        tag='?f=flair_name%3A"'+first_name+'"'
    else:
        tag='?f=flair_name%3A"'+first_name+'%20'+last_name+'"'
        if first_name == 'Laplus' and last_name == 'Darknesss':
            tag='?f=flair_name%3A"'+'La%2B'+'%20'+last_name+'"'
    replace_url = base_url+tag
    return replace_url