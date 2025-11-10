import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

# VARIABLES
username = "manuel.madeira"
password = "AlakaiRoofing123"
base_url = "https://www.publicpurchase.com"
keyword = "construction"


def create_driver():
    options = Options()
    options.add_argument("--headless=new")  # newer headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = uc.Chrome(service=service, options=options)
    return driver


def run_script():
    
    driver = create_driver()
    print("✅ ChromeDriver launched successfully", flush=True)
    

    try:
        # LOGIN
        driver.get("https://www.publicpurchase.com/gems/login/login")
        driver.find_element(By.NAME, "uname").send_keys(username)
        driver.find_element(By.NAME, "pwd").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "input[type='button']").click()

        try:
            WebDriverWait(driver, 15).until(
                EC.url_contains("https://www.publicpurchase.com/gems/vendor/home")
            )
            print("✅ Logged in successfully!")
        except:
            print("⚠️ Login might have failed or taken too long.")

        # SEARCH PAGE
        driver.get("https://www.publicpurchase.com/gems/browse/search")
        print("➡️ Navigated to search page.")

        driver.find_element(By.NAME, "bidTitle").send_keys(keyword)
        driver.find_element(By.ID, "searchButton").click()

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table.tabHome tbody tr.listA, table.tabHome tbody tr.listB")
                )
            )
            print("✅ Search successful: results table loaded!")
        except:
            print("⚠️ Search results did not load or took too long.")
            return

        # SCRAPE DATA
        results = []
        rows = driver.find_elements(By.CSS_SELECTOR, "table.tabHome tbody tr.listA, table.tabHome tbody tr.listB")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            title_element = cells[3].find_element(By.TAG_NAME, "a")
            title_text = title_element.text
            link = (
                base_url + title_element.get_attribute("href")
                if title_element.get_attribute("href").startswith("/")
                else title_element.get_attribute("href")
            )

            row_data = {
                "Bid Id": cells[0].text,
                "Agency": cells[1].text,
                "State": cells[2].text,
                "Title": title_text,
                "Type": cells[4].text,
                "Link": link
            }
            results.append(row_data)

        # POST RESULTS to the construction N8N node
        url = "https://n8n.srv988364.hstgr.cloud/webhook/e3ab4159-487e-44a8-9bd4-cfa949572f81"
        response = requests.post(url, json=results)

        print(f"Status code: {response.status_code}")
        print("Response text:", response.text)
        print(f"✅ Results retrieved successfully. Total results: {len(results)}")

    finally:
        driver.quit()


# RUN EVERY 1 HOUR
while True:
    print("\n🚀 Obtaining Public Purchase Contracts...\n")
    run_script()
    print("⏰ Waiting 1 hour before next run...\n")
    time.sleep(3600)  # 1 hour = 3600 seconds
















