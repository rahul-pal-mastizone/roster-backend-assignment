import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# CONFIG
BASE_URL = "https://www.behance.net"
SEARCH_URL = "https://www.behance.net/search/users?search="
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")
MAX_PROFILES_PER_ROLE = 50
MAX_SEARCH_PAGES = 10  # max pages to avoid long scraping

def is_valid_profile_url(url):
    parsed = urlparse(url)
    if not parsed.netloc.endswith("behance.net"):
        return False
    path = parsed.path.strip("/").split("/")[0]
    invalid_paths = ["studio", "media", "agency", "productions", "designs", "labs", "official",
                    "channel", "team", "llc", "inc", "pvt", "gmbh", "plc", "co", "company", "group", "The "]

    if path.lower() in invalid_paths or len(path) == 0:
        return False
    return True

def get_profile_links(role_query, max_profiles):
    profile_links = set()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    page = 1
    while len(profile_links) < max_profiles and page <= MAX_SEARCH_PAGES:
        url = f"{SEARCH_URL}{role_query}&page={page}"
        print(f"Scraping search page: {url}")
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'behance.net/')]"))
            )
        except:
            print("Timeout waiting for search results")
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'behance.net/')]")
        for elem in elements:
            href = elem.get_attribute("href")
            if href and is_valid_profile_url(href):
                profile_links.add(href.split('?')[0])  # remove tracking params
                if len(profile_links) >= max_profiles:
                    break
        page += 1
        time.sleep(2)

    driver.quit()
    return list(profile_links)[:max_profiles]

def extract_profile_data(driver, profile_url, role_type):
    try:
        driver.get(profile_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Clean name extraction:
        # 1) Try h1 tag - usually profile name
        name = None
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            name = h1.text.strip()
        else:
            # fallback to profile link last part (username style)
            path_parts = profile_url.strip('/').split('/')
            name = path_parts[-1].replace('-', ' ').title() if path_parts else "N/A"

        # Extract email if present (mailto links)
        email = ""
        for a in soup.find_all('a', href=True):
            if "mailto:" in a['href']:
                email = a['href'].replace("mailto:", "").strip()
                break

        return {
            "name": name,
            "email": email,
            "profile_link": profile_url,
            "role_type": role_type
        }
    except Exception as e:
        print(f"Error scraping {profile_url}: {e}")
        return None

def scrape_role(role_query, role_type, driver, max_profiles):
    print(f"Scraping role: {role_type}")
    profile_links = get_profile_links(role_query, max_profiles)
    print(f"Found {len(profile_links)} profiles for {role_type}")

    data = []
    for i, link in enumerate(profile_links, 1):
        print(f"[{i}/{len(profile_links)}] Extracting {link}")
        profile_data = extract_profile_data(driver, link, role_type)
        if profile_data:
            data.append(profile_data)
        time.sleep(1)

    return data

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        video_editors = scrape_role("video%20editor", "Video Editor", driver, MAX_PROFILES_PER_ROLE)
        thumbnails = scrape_role("thumbnail%20designer", "Thumbnails", driver, MAX_PROFILES_PER_ROLE)

        all_data = video_editors + thumbnails
        df = pd.DataFrame(all_data)

        # Remove duplicates by profile_link and email
        df.drop_duplicates(subset=['profile_link', 'email'], inplace=True)

        os.makedirs("data", exist_ok=True)
        df.to_csv("data/roster_scraped_profiles.csv", index=False)

        print("Done! CSV saved to data/roster_scraped_profiles.csv")

    finally:
        driver.quit()
