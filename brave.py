import requests
import json
from typing import List, Dict
from config import BRAVE_API_KEY

def brave_search(query: str, count: int = 5, search_lang: str = "en") -> dict:
    """
    Perform a Brave Web Search and return the full JSON response.
    """
    api_key = BRAVE_API_KEY
    if not api_key:
        raise RuntimeError("BRAVE_API_KEY environment variable not set")

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "search_lang": search_lang
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def extract_titles_and_descriptions(
    data: dict
) -> List[Dict[str, str]]:
    """
    From a Brave Search JSON response, pull out just the title and description
    of each 'web' result.
    """
    web_results = data.get("web", {}).get("results", [])
    reduced = []
    for item in web_results:
        title = item.get("title", "").strip()
        desc  = item.get("description", "").strip()
        # skip entries that lack both
        if title or desc:
            reduced.append({"title": title, "description": desc})
    return reduced

if __name__ == "__main__":
    # Make sure your environment has:
    #   export BRAVE_API_KEY="your_real_api_key"
    query = input("Enter your search query: ")
    try:
        full_response = brave_search(query, count=10)
        minimal = extract_titles_and_descriptions(full_response)
        print(json.dumps(minimal, indent=2))
    except Exception as e:
        print(f"Error: {e}")
