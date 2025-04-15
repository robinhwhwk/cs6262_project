import time
import csv
import os, subprocess, shutil
from selenium import webdriver
from selenium import webdriver
from chromedriver_py import binary_path # this will get you the path variable
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from datetime import datetime

FIREFOX_DRIVER_PATH = "/Users/robinhwhwk/Downloads/geckodriver"
EDGE_DRIVER_PATH = "/Users/robinhwhwk/Downloads/edgedriver_mac64/msedgedriver"
SAFARI_DRIVER_PATH = "/usr/bin/safaridriver"

def create_driver(browser):
    if browser == "Chrome":
        options = ChromeOptions()
        options.add_argument("--headless=new")
        service = ChromeService(executable_path=binary_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(20)
        
    if browser == "Firefox":
        options = FirefoxOptions()
        options.add_argument("--headless=new")
        # if we want to enable safe browsing
        # options.set_preference("browser.safebrowsing.enabled", True)
        service = FirefoxService(FIREFOX_DRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(20)
        
    if browser == "Edge":
        options = EdgeOptions()
        options.add_argument("--headless=new")
        service = EdgeService(EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
        driver.implicitly_wait(20)

    if browser == "Safari":
        options = SafariOptions()
        service = SafariService(SAFARI_DRIVER_PATH)
        driver = webdriver.Safari(service=service, options=options)
        driver.implicitly_wait(20)
    
    if browser == "Tor":
        os.system("""osascript -e 'tell app "Tor Browser" to open'""")
        tor_binary_path_driver = '/Applications/Tor\\ Browser.app/Contents/MacOS/firefox'
        geckodriver_path = FIREFOX_DRIVER_PATH

        proxy_settings = Proxy({
            'proxyType': ProxyType.MANUAL,
            'socksProxy': '127.0.0.1:9050',
            'socksVersion': 5
        })

        os.popen(tor_binary_path_driver)
        options = FirefoxOptions()
        options.proxy = proxy_settings
        options.headless = True

        service = FirefoxService(FIREFOX_DRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)

        driver.implicitly_wait(10)
    
    return driver

def check_phishing_block(driver, url):
    """ Returns 'Blocked' or 'Not Blocked' """
    try:
        driver.get(url)
        time.sleep(3)  # Let the page or warning load
        
        page_source = driver.page_source.lower()
        current_url = driver.current_url.lower()
        
        phishing_keywords = [
            "deceptive site",
            "phishing",
            "dangerous site",
            "not secure",
            "potential security risk",
            "your connection is not private",
            "this site has been reported as unsafe", 
            "secure connection failed"
        ]

        for keyword in phishing_keywords:
            if keyword in page_source:
                print(f"{url} blocked", flush=True)
                return "Blocked"
        print(f"{url} not blocked", flush=True)
        return "Not Blocked"
    
    except Exception as e:
        print(f"Exception checking URL: {url}, {e}")
        # If there's an error, consider it not blocked or log as error
        return "Error"

if __name__ == "__main__":

    phishing_urls = []
    try:
        with open("feeds.txt", 'r') as file:
            for url in file:
                phishing_urls.append(url.rstrip('\n'))
    except FileNotFoundError:
        print("Error: File not found")

    
    # browsers = ["Chrome", "Edge", "Firefox", "Safari"]
    browsers = ["Tor"]
    for browser in browsers:
        results = []
        driver = create_driver(browser)
        for url in phishing_urls:
            result = check_phishing_block(driver, url)
            results.append({
                "browser": browser,
                "url": url,
                "result": result,
            })
        if browser == "Tor":
            subprocess.call(['osascript', '-e', 'tell application "Tor Browser" to quit'])
        driver.quit()
        output_dir = os.path.join("results", browser)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        
        with open(os.path.join(output_dir, "phishing_test_results.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["browser", "url", "result"])
            writer.writeheader()
            for row in results:
                writer.writerow(row)

    print("Test complete. Results saved to phishing_test_results.csv")
