from selenium import webdriver


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import openpyxl




pages_source = []
name_set = set()
main_list = []
url = 'https://yandex.ru/maps/org/makdonalds/35349117035/reviews/?ll=37.679803%2C55.746821&z=15'

def start():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    return driver

def click_in_filters(num, driver):
    business_reviews = driver.find_elements(By.CLASS_NAME, "business-reviews-card-view__review")
    time.sleep(2)
    business_reviews[0].click()
    time.sleep(2)
    main_button = driver.find_element_by_xpath('//*[@class="card-section-header__right-content"]')
    time.sleep(2)
    main_button.click()
    time.sleep(2)
    filters = driver.find_elements_by_xpath('//*[@class="rating-ranking-view__popup-line"]')
    time.sleep(2)
    filters[num].click()
    time.sleep(5)

def seleniun_get_all_reviews(driver):
    print("Начал нажимать на кнопку посмотреть еще отзывы.")
    time.sleep(3)
    count_rev = driver.find_element(By.CLASS_NAME, "card-section-header__title").text
    count_rev = int(count_rev.split()[0])
    if count_rev < 600:
        count_data = count_rev
    else:
        count_data = 600
    time.sleep(2)
    business_reviews = driver.find_elements(By.CLASS_NAME, "business-reviews-card-view__review")
    while len(business_reviews)!=count_data:
        click_el = driver.find_elements(By.CLASS_NAME, "business-reviews-card-view__skeleton-body")
        time.sleep(2)
        click_el[0].click()
        time.sleep(2)
        business_reviews = driver.find_elements(By.CLASS_NAME, "business-reviews-card-view__review")
    time.sleep(3)
    
    pages_source.append(driver.page_source)


def parse_page_source(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    all_items = soup.find_all('div', class_="business-reviews-card-view__review")
    for i in all_items:
        name = i.find("span", attrs={"itemprop": "name"}).text
        not_stars = i.find_all("span", attrs={"class": "_empty"})
        not_stars = len(not_stars)
        if not_stars == 0:
             not_stars = 0
        like_dislike = i.find_all("div", attrs={"class": "business-reactions-view__container"})
        like = like_dislike[0].find("div")
        dislike = like_dislike[1].find("div")
        if like == None:
            like = 0
        else:
            like = like.text
        if dislike == None:
            dislike = 0
        else:
            dislike = dislike.text
        
        review = i.find("span", attrs={"class": "business-review-view__body-text"}).text
        pub_date = i.find("span", attrs={"class": "business-review-view__date"}).span.text
        status = i.find("div", attrs={"class": "business-review-view__author-profession"})
        if status == None:
            status = "Нет"
        else:
            status = status.text
        print("name: " + name)
        name_set.add(name)
        if len(name_set) != len(main_list):
            main_list.append([str(name), str(status), str(review), str(like), str(dislike), str(5-not_stars), str(pub_date)])

def main():
    driver = start()
    seleniun_get_all_reviews(driver)
    driver.get(url)
    click_in_filters(-1, driver)
    seleniun_get_all_reviews(driver)
    driver.get(url)
    click_in_filters(-2, driver)
    seleniun_get_all_reviews(driver)
    driver.get(url)
    click_in_filters(-3, driver)
    seleniun_get_all_reviews(driver)
    driver.close()
    for page_source in pages_source:
        parse_page_source(page_source)
    print(name_set)
    convertor(main_list)

def convertor(data):
    print(data)
    df = pd.DataFrame(data, columns=['Name', 'Status', 'Review', 'Like', 'Dislike', 'Stars', "Date publication"])
    df.to_excel('./main.xlsx', sheet_name="main_1")

main()
