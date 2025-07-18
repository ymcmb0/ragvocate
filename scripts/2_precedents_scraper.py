import os
import json
import time
import requests
from bs4 import BeautifulSoup
import serpapi
from dotenv import load_dotenv
load_dotenv()
SERPAPI_KEY = "2cf46e4ff2848fe942fe63c05b153aea322fced94dfe01a91425700edd1aa0a5"  # Sign up at serpapi.com (free tier works)

CASE_NAMES = [
    "US v. Wong Kim Ark",
    "Kwong Hai Chew v. Colding",
    "Shaughnessy v. US ex rel Mezei",
    "Graham v. Department of Public Welfare",
    "Kleindienst v. Mandel",
    "Matthews v. Diaz",
    "Fiallo v. Bell",
    "Toll v. Moreno",
    "Vance v. Terrazas",
    "Landon v. Plasencia",
    "Plyler v. Doe",
    "INS v. Lopez-Mendoza",
    "INS v. Delgado",
    "INS v. Cardoza-Fonseca",
    "INS v. Elias-Zacarias",
    "Vartelas v. Holder"
]


SAVE_DIR = os.getenv("PRECEDENTS_RAW_TEXT")
os.makedirs(SAVE_DIR, exist_ok=True)


def get_lii_link(case_name):
    """Use SerpAPI to find LII page for a case."""
    params = {
        "q": f"{case_name} site:law.cornell.edu",
        "api_key": SERPAPI_KEY,
        "engine": "google"
    }
    search = serpapi.search(params)
    results = search.as_dict()
    for res in results.get("organic_results", []):
        link = res.get("link", "")
        if "law.cornell.edu" in link:
            return link
    return None


def fetch_summary(url):
    """Scrape the summary from a LII case page."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Heuristics for content - may vary per case
        content = soup.find("div", class_="content") or soup.find("main")
        if not content:
            return None

        paragraphs = content.find_all("p")
        summary_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return summary_text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


for case in CASE_NAMES:
    print(f"🔍 Searching for: {case}")
    link = get_lii_link(case)
    if not link:
        print(f"No link found for {case}")
        continue

    print(f"Scraping: {link}")
    summary = fetch_summary(link)
    if summary:
        filename = os.path.join(SAVE_DIR, case.replace(" ", "_").replace(".", "").replace("/", "") + ".txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Saved: {filename}")
    else:
        print(f"No summary extracted for {case}")

    time.sleep(2)  # respectful crawling
