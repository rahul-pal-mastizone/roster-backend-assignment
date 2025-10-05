# 🧾 Roster Backend Assignment – Behance Scraper

## 📌 Overview

This project scrapes public profiles of **Video Editors** and **Thumbnail Designers** from [Behance.net](https://www.behance.net) to generate a clean, structured CSV file.

## ⚙️ Technologies Used

- **Python**
- **Selenium** – to render and browse JavaScript-powered pages
- **BeautifulSoup** – for parsing HTML
- **Pandas** – for data handling and export
- **Chrome WebDriver**

---

## 🔍 What It Does

1. **Searches Behance** for profiles using specific keywords (e.g., `video editor`, `thumbnail designer`)
2. **Collects up to 50 profiles per role**
3. **Extracts**:
   - Name (from profile page)
   - Email (if available)
   - Profile Link
   - Role Type
4. **Filters out invalid or duplicate profiles**
5. **Saves the results to CSV**:  
   `data/roster_scraped_profiles.csv`

---

## 📁 Output

CSV File: `roster_scraped_profiles.csv`  
With columns:

| name | email | profile_link | role_type |
|------|-------|--------------|-----------|

---

## 🧠 Notes

- The scraper is polite: adds delays (`sleep(1)`) and avoids overloading servers.
- Emails are only included if they are publicly listed in `mailto:` links.
- JavaScript-heavy pages are rendered via Selenium (headless Chrome).
- Runs for up to **50 profiles per role** using pagination.

---

## 🚀 Setup & Run

### 1. Install Dependencies

```bash
pip install selenium beautifulsoup4 pandas


2. Download ChromeDriver

Download from: https://chromedriver.chromium.org/downloads

Make sure the version matches your Chrome browser.

Place it in the same directory as scraper.py or update the path in the code.

3. Run the Script
python scraper.py

🕒 Time Spent

Approx. 3 hours (including scraping, testing, filtering, and cleaning the data)

📈 Scalability Tips

To scrape more profiles efficiently:

Increase the MAX_SEARCH_PAGES or MAX_PROFILES_PER_ROLE

Use concurrent requests (aiohttp, asyncio)

Add proxy rotation to bypass rate limits

📌 Author

This website was designed, developed, and maintained by Rahul Pal.

---
#
