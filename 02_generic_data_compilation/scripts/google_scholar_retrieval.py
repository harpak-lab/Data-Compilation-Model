import time
import random
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up a headless Chrome browser using Selenium
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Perform Google Scholar search with the given query
def search_scholar(driver, query):
    search_url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(random.uniform(2, 4))

# Extract title, result link, and PDF (if available) from search results
def extract_papers(driver, max_results=5):
    papers = []
    results = driver.find_elements(By.CSS_SELECTOR, 'div.gs_ri')[:max_results]

    for idx, result in enumerate(results):
        title_el = result.find_element(By.CSS_SELECTOR, 'h3.gs_rt')
        title = title_el.text
        try:
            link = title_el.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = "No direct link available"

        # Find PDF link if available
        try:
            pdf_el = driver.find_elements(By.CSS_SELECTOR, "div.gs_or_ggsm")[idx]
            pdf_link = pdf_el.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            pdf_link = None

        papers.append({"title": title, "link": link, "pdf_link": pdf_link})

    return papers

# Attempt to download PDFs from the extracted paper entries
def download_pdfs(papers, folder="02_generic_data_compilation/downloads"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    for paper in papers:
        if paper["pdf_link"]:
            try:
                response = requests.get(paper["pdf_link"])
                if response.status_code == 200:
                    filename = paper["title"][:50].replace('/', '_').replace('\\', '_') + ".pdf"
                    with open(os.path.join(folder, filename), "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print("STATUS CODE: ", response.status_code)
            except Exception as e:
                print(f"Failed to download PDF for: {paper['title']}. Error: {e}")

# Main driver for Scholar scraping workflow
def main():
    query = input("Enter your Google Scholar search query: ").strip()
    driver = setup_driver()

    try:
        search_scholar(driver, query)
        papers = extract_papers(driver)
        for i, p in enumerate(papers, 1):
            print(f"\nPaper {i}")
            print(f"Title: {p['title']}")
            print(f"Link: {p['link']}")
            print(f"PDF: {p['pdf_link'] if p['pdf_link'] else 'No PDF available'}")

        download_pdfs(papers)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()