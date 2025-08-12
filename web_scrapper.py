import time
import re
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Note:(1)download the requests library on your pc or laptop to run
# Download Instructions: 1. Open your terminal or command prompt 2. type "pip install requests" and "pip install selenium" 3. press enter 4.Wait for download to finished
# Note:(2)Work for SSL Verification and js rendering website

# Made by Narihito (A.K.A Hein Htet Aung TNT-2409)




#InsecureRequestWarning for requests verify=False (New Method)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# web browser suitability
def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    ]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

# Session Request
session = requests.Session()

# function to scrap using Selenium Import library with web driver
def scrape_with_selenium(url: str):
    try:
        options = Options()
        options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)  
        html = driver.page_source
        driver.quit()
        return html
    except WebDriverException as e:
        print(f"Selenium error for {url}: {e}")
        return "-1"

# Request function: (updated for SSL verification and js rendering)
def request_by_module_requests(url: str):
    print(f"Using With Selenium...")
    html = scrape_with_selenium(url)
    if html != "-1":
        return html
    print("Selenium failed or not available, fallback to requests")
    headers = get_random_headers()
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            time.sleep(random.uniform(1, 3))
            response = session.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Attempt {attempt} failed for {url}: {e}")
            if attempt == retries:
                print("Max retries reached, skipping.")
                return "-1"
            time.sleep(2)

#scrapper function run

def run_scraper(url: str, auto_refresh: bool = False, refresh_interval: int = 60, refresh_times: int = 1):
    count = 0
    while True:
        print("Links found on " f"{url}:")
        html = request_by_module_requests(url)
        if html == "-1":
            print("Failed to retrieve the page.")
            return

        links = re.findall(r'<a\s+(?:[^>]*?\s+)?href=["\'](.*?)["\'](?:[^>]*)>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        for href, text in links:
            clean_text = re.sub('<.*?>', '', text).strip()
            if clean_text and href:
                print(f"Header Website: {clean_text} | URL: {href}")
        count += 1
        if not auto_refresh or count >= refresh_times:
            break
        print(f"Refreshing in {refresh_interval} seconds... ({count}/{refresh_times})")
        time.sleep(refresh_interval)

#user input validation areas

def get_valid_int(prompt, min_value=1, max_value=600):
    while True:
        user_input = input(prompt)
        if user_input.strip() == "":
            return min_value
        try:
            value = int(user_input)
            if value < min_value or value > max_value:
                print(f"Please enter a number between {min_value} and {max_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_yes_no(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", "y"]:
            return True
        elif user_input in ["no", "n"]:
            return False
        else:
            print("Input Only yes/y or no/n")

def main():
    url_input = input("Enter the URL to scrape (no need to include https://): ")
    if not url_input.startswith("http://") and not url_input.startswith("https://"):
        url = "https://" + url_input
    else:
        url = url_input
    auto_refresh = get_yes_no("Enable auto-refresh? (yes/no or y/n): ")
    refresh_interval = get_valid_int("Enter refresh interval (in seconds up to 60): ", 1, 60)
    refresh_times = 1
    if auto_refresh:
        refresh_times = get_valid_int("Enter how many times to refresh the page: ", 1, 1000)
    run_scraper(url, auto_refresh, refresh_interval, refresh_times)
    print("Scraping complete.")

if __name__ == "__main__":
    main()

