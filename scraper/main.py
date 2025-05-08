import os
import json
import time
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
start_url = "https://www.bestbuddies.org.qa/"
faq_base_url = "https://www.bestbuddies.org.qa/en/faq"
domain = urlparse(start_url).netloc
output_base = "website_content"
visited = set()
to_visit = [start_url]

# Set up Selenium (headless Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)

def extract_internal_links(url, soup):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(url, a_tag['href'])
        parsed_url = urlparse(full_url)
        if parsed_url.netloc == domain:
            clean_url = full_url.split("#")[0]
            links.add(clean_url)
    return links

def clean_text(soup):
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def safe_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    query = parsed.query.replace("=", "_").replace("&", "_")
    if not path:
        path = "index"
    filename = f"{path}_{query}" if query else path
    if filename.endswith("/"):
        filename += "index"
    return os.path.join(output_base, filename + ".json")

def save_page_as_json(url, title, body):
    file_path = safe_filename_from_url(url)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({
            "url": url,
            "title": title,
            "body": body
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved: {file_path}")

def get_page_content(url):
    driver.get(url)
    time.sleep(3)
    return driver.page_source

def extract_faq_pages(start_faq_url):
    print("📄 Extracting all FAQ pages...")
    faq_urls = set()
    driver.get(start_faq_url)
    time.sleep(3)
    faq_urls.add(driver.current_url)

    while True:
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
            )
            next_btn.click()
            time.sleep(2)
            current_url = driver.current_url
            if current_url not in faq_urls:
                faq_urls.add(current_url)
            else:
                break
        except:
            break

    print(f"🔗 Found {len(faq_urls)} FAQ pages.")
    return faq_urls

def save_urls_to_csv(filename, urls):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL"])
        for url in sorted(urls):
            writer.writerow([url])
    print(f"📄 Saved {len(urls)} URLs to {filename}")

# Add dynamic FAQ pages to the crawl list
faq_pages = extract_faq_pages(faq_base_url)
for url in faq_pages:
    if url not in to_visit and url not in visited:
        to_visit.append(url)

# Main crawl loop
while to_visit:
    current_url = to_visit.pop(0)
    if current_url in visited:
        continue

    print(f"🔍 Visiting: {current_url}")
    visited.add(current_url)

    try:
        response = requests.get(current_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
        else:
            html = get_page_content(current_url)
            soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title else ""
        body = clean_text(soup)
        save_page_as_json(current_url, title, body)

        new_links = extract_internal_links(current_url, soup)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        time.sleep(1)

    except Exception as e:
        print(f"❌ Failed: {current_url}\n    Reason: {e}")

# Save visited and remaining URLs
save_urls_to_csv("visited_urls.csv", visited)
save_urls_to_csv("to_visit_urls.csv", to_visit)

print("\n🎉 Done crawling and saving all pages.")
driver.quit()