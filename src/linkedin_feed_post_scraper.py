import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import date, datetime
from selenium.common.exceptions import NoSuchElementException

import time
import os
import pandas as pd
import csv

#Set personal info to use on linkedin.
email = ''
password = ''
#Set keyword id to scraping.
#['leader', 'manage', 'team', 'organization', 'service', 'power', 'servant', 'control', 'steward', 'govern']
keyword = 'leader'
target = 1000

if __name__ == '__main__':
    driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install())

    #Sign in linkedin with email address and password.
    driver.get('https://www.linkedin.com/checkpoint/lg/sign-in-another-account')
    input_email = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="username"]'))).send_keys(email)
    input_password = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).send_keys(password)
    signin = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="organic-div"]/form/div[3]/button'))).click()
    time.sleep(1)


    path = f'./scraped_data/{keyword}.csv'
    check_file = os.path.exists(path)
    if check_file:
        df = pd.read_csv(path)
        print("Current extracted data size  ", len(df))
        perfect = len(df)
    else:
        with open(path, 'w', newline='') as file:
            write = csv.writer(file)
            write.writerow(['id', 'name', 'description', 'date'])
            file.close()
        perfect = 0
    
    driver.get('https://linkedin.com/feed')
    time.sleep(3)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="global-nav-typeahead"]/input'))).send_keys(keyword)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="global-nav-typeahead"]/input'))).send_keys(Keys.ENTER)
    
    for button_id in range(1, 10):
        if WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="search-reusables__filters-bar"]/ul/li[{button_id}]/button'))).text == "Posts":
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="search-reusables__filters-bar"]/ul/li[{button_id}]/button'))).send_keys(Keys.ENTER)
            break
        time.sleep(5)

    print("extracted data number is ", perfect)

    current_id = 0

    with open(path, 'a',newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        
        for lump in range(1, 100000):
            wait_time = 10
            while wait_time < 30:
                try:
                    WebDriverWait(driver, 50).until(EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="scaffold-finite-scroll__content"]/div[{lump}]')))
                    print("sucess lump ", lump)
                    break
                except:
                    time.sleep(1)
                    WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.XPATH, '/html/body'))).send_keys(Keys.END)
                    print("wait for 10 seconds")
                    time.sleep(wait_time)
                    wait_time += 1
            if wait_time == 30:
                print("The scraping was completed.")
                break
            for k in range(1, 11):
                print(lump, k)
                try:
                    name = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//div[@class='scaffold-finite-scroll__content']/div[{lump}]/div/ul/li[{k}]/div/div/div/div[2]/a/div[3]/span[1]/span[1]/span[1]"))).text
                    print("name   ", name)
                    current_id += 1
                except:
                    break

                if current_id <= perfect:
                    continue

                try:
                    description = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//div[@class='scaffold-finite-scroll__content']/div[{lump}]/div/ul/li[{k}]/div/div/div/div[4]/div/div/span/span"))).text
                    description = description.replace('\n', ' ')
                except:
                    description = ""
                    print("empty description")
                
                try:
                    ago = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//div[@class='scaffold-finite-scroll__content']/div[{lump}]/div/ul/li[{k}]/div/div"))).get_attribute("data-urn")
                    posted = datetime.fromtimestamp(int((str(bin(int(ago[-19:])))[2:43]), 2) / 1000).strftime("%m/%d/%Y-%H:%M:%S")
                    print(posted)
                except:
                    posted = ""
                    print("empty date")

                if current_id == perfect + 1:
                    print("current number of extracted post is ", current_id)
                    print(perfect, name, description, posted)
                    writer.writerow([perfect, name, description, posted])
                    perfect += 1
                if perfect == target:
                    break
                WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.XPATH, '/html/body'))).send_keys(Keys.END)
                time.sleep(1)
            if perfect == target:
                break
