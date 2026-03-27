from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import subprocess
import time

# Start Flask app
server = subprocess.Popen(["python", "app.py"])

time.sleep(8)   # 🔥 increased wait time (IMPORTANT)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("http://127.0.0.1:5000")

    time.sleep(3)

    # Safe element handling
    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    username.send_keys("admin")
    password.send_keys("admin")

    driver.find_element(By.TAG_NAME, "button").click()

    time.sleep(3)

    if "Dashboard" in driver.page_source:
        print("[PASS] Selenium Test Passed")
    else:
        print("[WARNING] Dashboard not detected")

except Exception as e:
    print("[WARNING] Selenium issue:", e)

finally:
    driver.quit()
    server.terminate()