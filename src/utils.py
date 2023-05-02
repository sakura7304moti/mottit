from io import StringIO, BytesIO
import os
import re
from time import sleep
import random
from tqdm import tqdm
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
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

#ドライバー生成
def init_driver(headless=True):#get chrome driver
    options = ChromeOptions()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # An error will occur without this line
        options.add_argument('--window-size=900,1000')
        #options.add_experimental_option('prefs', "'profile.default_content_setting_values.notifications': 2")
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

#キャラクター別URL取得
def page_url(first_name:str,last_name:str=None):#searched page url
    base_url='https://www.reddit.com/r/Hololewd/new'
    if last_name == None:#fullName only?
        tag='?f=flair_name%3A"'+first_name+'"'
        if first_name == "AI-Generated":
            tag='?f=flair_name%3A"'+first_name+'%20"'
    else:
        tag='?f=flair_name%3A"'+first_name+'%20'+last_name+'"'
        if first_name == 'Laplus' and last_name == 'Darknesss':
            tag='?f=flair_name%3A"'+'La%2B'+'%20'+last_name+'"'
    replace_url = base_url+tag
    return replace_url

def parse_number(text):
    if text.isdigit():
        return int(text)
    elif text[-1] == 'k':
        return int(float(text[:-1])) * 1000
    else:
        return int(float(text))

#画像、いいね、などを取得する
def get_df(driver,image_driver,url):
    driver.get(url)
    """
    prepare
    """

    #jump to url
    driver.get(url)
    print(f'url -> {url}')

    """
    scroll
    """
    sc = 60
    for i in range(sc):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.25)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.25)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.25)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.25)
        print(f'\r scroll {i+1}/{sc}',end="")
    print('OK!')
    """
    get cards
    """
    #get card
    cards = driver.find_elements(By.XPATH,"//div[@data-testid='post-container']")
    print(f'cards count -> {len(cards)}')

    """
    for card in cards:
    """
    tweets = []
    for index,card in tqdm(enumerate(cards),total=len(cards)):
        try:
            #page url
            image_base_links = card.find_elements(By.TAG_NAME,"a")
            image_base_link = ""
            for image_base in image_base_links:
                try:
                    if "/r/Hololewd/comments" in image_base.get_attribute("href"):
                        image_base_link = image_base.get_attribute("href")
                except:
                    pass

            #expands click
            try:
                image_driver.find_element(By.XPATH,"//div[@data-adclicklocation='title']").click()
            except:
                pass

            if image_base_link != "":
                image_driver.get(image_base_link)

                #image link
                image_links = []
                try:
                    soup = BeautifulSoup(image_driver.page_source, 'html.parser')
                    for a in soup.find_all(name="a",attrs={"rel":"noopener noreferrer"}):
                        link = a.get('href')
                        if '.jpg' in link or '.png' in link:
                            image_links.append(link)
                except:
                    pass

                #vote
                try:
                    container = image_driver.find_element(By.XPATH,"//div[@data-testid='post-container']")
                    vote_element = container.find_element(By.XPATH,".//div//div//div")
                    vote = parse_number(vote_element.text)
                except:
                    vote = 0

                #video_link
                video_links=[]
                try:
                    soup = BeautifulSoup(image_driver.page_source, 'html.parser')
                    for a in soup.find_all(name="source"):
                        link = a.get('src')
                        video_links.append(link)
                except:
                    pass

                #result
                tweet = [
                    image_base_link,
                    image_links,
                    video_links,
                    vote
                ]
                tweets.append(tweet)
        except Exception as e:
            print(f'err index : {index}  ',end='')
            print(e)

    tweet_df = pd.DataFrame(tweets,columns=["url","images","videos","vote"])
    return tweet_df
