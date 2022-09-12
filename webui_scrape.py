import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
CHROMEDRIVER_PATH = '/home/mgiordano/Downloads/chromedriver'

def get_results(search_term):
    url = 'https://www.imdb.com/find'
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)
    # browser = webdriver.Chrome(CHROMEDRIVER_PATH)
    driver.get(url)
    search_box = driver.find_element(By.ID, 'suggestion-search')
    search_box.send_keys(search_term)
    search_box.submit()
    links = driver.find_elements(By.CLASS_NAME, 'findResult')
    results = []
    for link in links:
        href = link.text
        print(href)
        results.append(href)
    driver.quit()
    return results

get_results('south park')
