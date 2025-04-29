import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
ZOTERO_USER_ID = os.getenv("ZOTERO_USER_ID")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")

def search_scholar(query, max_results=5):
    print(f"Searching Google Scholar for '{query}'...")

    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": max_results
    }

    response = requests.get("https://serpapi.com/search.json", params=params)
    data = response.json()

    papers = []
    if "organic_results" in data:
        for result in data["organic_results"][:max_results]:
            title = result.get("title")
            link = result.get("link")
            doi = None

            # try to find a DOI from different places
            link = result.get('link', '')
            doi = None

            # "doi/abs/" in the link
            if "doi/abs/" in link:
                doi = link.split("doi/abs/")[-1].split('?')[0]

            # "doi.org/" in publication_info
            if not doi and 'publication_info' in result:
                pub_info = result['publication_info'].get('summary', '')
                if "doi.org/" in pub_info:
                    doi = pub_info.split("doi.org/")[-1].split()[0]

            # main link directly has "doi.org/"
            if not doi and "doi.org/" in link:
                doi = link.split("doi.org/")[-1].split('?')[0]

            # resource links
            if not doi and 'resources' in result:
                for resource in result['resources']:
                    if 'doi.org/' in resource.get('link', ''):
                        doi = resource['link'].split("doi.org/")[-1].split('?')[0]

            papers.append({"title": title, "link": link, "doi": doi})

    return papers

def add_to_zotero(papers):
    headers = {
        "Zotero-API-Key": ZOTERO_API_KEY,
        "Content-Type": "application/json"
    }

    for paper in papers:
        if paper['doi']:
            print(f"Adding to Zotero by DOI: {paper['doi']} ({paper['title']})")

            payload = [
                {
                    "itemType": "journalArticle",
                    "DOI": paper['doi']
                }
            ]

            url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/items"
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200 or response.status_code == 201:
                print(f"Successfully added: {paper['title']}")
            else:
                print(f"Failed to add {paper['title']}: {response.status_code} {response.text}")
            time.sleep(1)
        else:
            print(f"No DOI found for {paper['title']} — skipping.")

def main():
    query = input("Enter your Google Scholar search query: ").strip()
    papers = search_scholar(query)

    for idx, paper in enumerate(papers, 1):
        print(f"\nPaper {idx}:")
        print(f"Title: {paper['title']}")
        print(f"Link: {paper['link']}")
        print(f"DOI: {paper['doi'] if paper['doi'] else 'No DOI found'}")

    add_to_zotero(papers)

if __name__ == "__main__":
    main()