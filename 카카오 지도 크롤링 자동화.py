import os
from selenium import webdriver
import requests
import csv
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException

가게이름 = "서울시 코인세탁소"

options = webdriver.ChromeOptions() # 크롬 브라우저 옵션
# options.add_argument('headless') # 브라우저 안 띄우기
options.add_argument('lang=ko_KR') #  KR 언어
chromedriver_path = "chromedriver" # 크롬 드라이버 위치
driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)
driver.get('https://map.kakao.com/')
driver.find_element_by_id("search.keyword.query").send_keys(가게이름)
driver.find_element_by_id("search.keyword.query").send_keys(Keys.ENTER)
time.sleep(4)
driver.execute_script("window.scrollTo(0,1080)") #스크롤 내리기

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
time.sleep(3)

#전역 변수
sing_room = []
adress_room = []
adressb_room = []
ba=[]
#점포명 , 주소, 도로명 주소 얻어오는 함수.
def get_name(sing,adress,adressb):
    for i in sing:
        sing_room.append(i.get_text())
    for i in adress:
        adress_room.append(i.get_text())
    for i in adressb:
        adressb_room.append(i.get_text())

def get_adress(): #실행시 가장 첫번째 페이지만 가져오는 함수.
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    sing = soup.find_all("a", attrs={"class": "link_name"})  # 노래방 이름 찾기
    adress = soup.find_all("p", attrs={"data-id": "otherAddr"})  # 노래방 주소 찾기
    ROADadress = soup.find_all("p", attrs={"data-id": "address"})
    get_name(sing,adress,ROADadress)
try:
    get_adress() #검색한 현 1페이지만 긁어오기.
    driver.find_element_by_xpath('//*[@id="info.search.place.more"]').send_keys(Keys.ENTER) #위치더보기 클릭하면 2페이지로 자동으로 넘어감.
    time.sleep(2)
    a = 1
    naljiBreak = True #이중 for문 탈출.
    # 2~ 5페이지 읽기
    for i in range(2, 6):
        if i == 5:
            xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
            driver.find_element_by_xpath(xPath).send_keys(Keys.ENTER)
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            sing = soup.find_all("a", attrs={"class": "link_name"})  # 노래방 이름 찾기
            adress = soup.find_all("p", attrs={"data-id": "otherAddr"})  # 노래방 주소 찾기
            adressb = soup.find_all("p", attrs={"data-id": "address"})
            get_name(sing,adress,adressb)
            driver.find_element_by_id("info.search.page.next").send_keys(Keys.ENTER) #다음버튼을 누른다.
            while True: #6페이지부터 페이지 끝까지 크롤링.
                if a == 6: #a 는 1씩 증감시키며 a가 6으로 증감시 다시 1로 되돌려준다.
                    a = 1  # a가 5면 다시 1로 초기화시켜준다.
                    if ' '.join(soup.find("button", attrs={"id": "info.search.page.next"})['class']) == "next disabled":
                        naljiBreak = False
                        break
                    else:
                        driver.find_element_by_id("info.search.page.next").send_keys(Keys.ENTER)  # a가 5가되면 다음버튼을 눌러준다.
                else:
                    pass
                if naljiBreak == False:
                    break
                xPath = '//*[@id="info.search.page.no' + str(a) + '"]'
                driver.find_element_by_xpath(xPath).send_keys(Keys.ENTER) #페이지(a)를 누른다.
                time.sleep(2)
                a = a + 1
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                sing = soup.find_all("a", attrs={"class": "link_name"})  # 노래방 이름 찾기
                adress = soup.find_all("p", attrs={"data-id": "otherAddr"})  # 노래방 주소 찾기
                adressb = soup.find_all("p", attrs={"data-id": "address"})
                get_name(sing, adress, adressb)
        if naljiBreak == False:
            break
        xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
        driver.find_element_by_xpath(xPath).send_keys(Keys.ENTER)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        sing = soup.find_all("a", attrs={"class": "link_name"})
        adress = soup.find_all("p", attrs={"data-id": "otherAddr"})
        adressb= soup.find_all("p", attrs ={"data-id":"address"})
        get_name(sing,adress,adressb)
except ElementNotInteractableException:
    print('not found')
for i in adress_room:
    ba.append(i.replace("(지번)", '').strip())
df1 = pd.DataFrame({'가게': sing_room,'주소': ba,'도로명주소': adressb_room})
df1.to_csv(f"{가게이름}.csv", mode='w',encoding='cp949',index=False)