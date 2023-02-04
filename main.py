from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import urllib.request
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import streamlit as st
headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'
        }
def openbs(url):
    time.sleep(1)
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    bs = BS(response, 'lxml', from_encoding='utf-8')
    return bs


def extract(obj, css):
    result = obj.select(css)
    if len(result) > 0:
        result = result[0].get_text().strip()
    else:
        result = ''
    return result


@st.experimental_singleton
def launch_driver(headless=False, image=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-desktop-notifications')
    options.add_argument("--disable-extensions")
    options.add_argument('--lang=ja')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if not image:
        options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    return driver


class Page:
    def __init__(self, group, name, category, target_const, amount, target_house, target, hpurl, tel, date):
        self.group = group
        self.name = name
        self.category = category
        self.target_const = target_const
        self.amount = amount
        self.target_house = target_house
        self.target = target
        self.hpurL = hpurl
        self.tel = tel
        self.date = date


    def __repr__(self):
        return self.name


def collect_urls():
    main_url = 'https://www.j-reform.com/reform-support/'
    driver = launch_driver(headless=True)
    driver.get(main_url)
    time.sleep(1)
    driver.execute_script('arguments[0].click();', driver.find_element(By.CSS_SELECTOR, 'input[value="3"]'))
    time.sleep(1)
    driver.execute_script('arguments[0].click();', driver.find_element(By.CSS_SELECTOR, 'input[value="4"]'))
    time.sleep(1)
    driver.execute_script('arguments[0].click();', driver.find_elements(By.CSS_SELECTOR, 'input[value="1"]')[-1])
    time.sleep(1)
    driver.execute_script('arguments[0].click();', driver.find_element(By.CSS_SELECTOR, 'input[alt="検索"]'))
    time.sleep(1)
    num_hits = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.num')))
    num_hits = int(num_hits.text)
    num_pages = int(np.ceil(num_hits/50))
    page_urls = [item.get_attribute('href') for item in driver.find_elements(By.CSS_SELECTOR, 'table.tbl-kekkalist td a')]
    #! 2ページのみ
    for page_num in range(1, 2):
        driver.execute_script('arguments[0].click();', driver.find_element(By.CSS_SELECTOR, 'a[title="next page"]'))
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.tbl-kekkalist td a')))
        page_urls.extend([item.get_attribute('href') for item in driver.find_elements(By.CSS_SELECTOR, 'table.tbl-kekkalist td a')])
    driver.quit()
    return page_urls


def scrape(page_urls):
    pages = []
    status_text = st.empty()
    progress_bar = st.progress(0)
    #! 10件のみ
    for i, page_url in enumerate(page_urls[:10]):
        bs = openbs(page_url)
        group = extract(bs, 'td.tbl-shosaittl-td1:contains("実施地方公共団体")+td')
        name = extract(bs, 'td.tbl-shosaittl-td1:contains("制度名（事業名）")+td')
        category = extract(bs, 'td.tbl-shosai-td1:contains("支援分類")+td')
        target_const = extract(bs, 'td.tbl-shosai-td1:contains("対象工事")+td p.shosai-cap')
        amount = extract(bs, 'td.tbl-shosai-td1:contains("補助率等")+td')
        target_house = extract(bs, 'td.tbl-shosai-td1:contains("対象住宅")+td')
        target = extract(bs, 'td.tbl-shosai-td1:contains("発注者")+td p.shosai-cap')
        try:
            hpurl = bs.select_one('td.tbl-shosai-td1:contains("詳細ホームページ")+td a')['href']
        except:
            hpurl = ''
        tel = extract(bs, 'td.tbl-shosai-td1:contains("お問合せ先")+td')
        date = extract(bs, 'td.tbl-shosai-td1:contains("最終更新日")+td')
        pages.append(Page(group, name, category, target_const, amount, target_house, target, hpurl, tel, date))
        progress_bar.progress((i+1)/10)
    df = pd.DataFrame([vars(item) for item in pages])
    df.columns = ['実施地方公共団体', '制度名（事業名）', '支援分類', '対象工事', '補助率等', '対象住宅', '発注者', '詳細ホームページ', 'お問合せ先', '最終更新日']
    return df