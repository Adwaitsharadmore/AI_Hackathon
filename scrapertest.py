import json
from bs4 import BeautifulSoup
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Configuration
JSON_FILE_PATH = Path('/Users/aryanredhu/hackathon/AI_Hackathon/output/all_output.json')
URLS_FILE_PATH = Path('/Users/aryanredhu/hackathon/AI_Hackathon/output/urls.txt')

def extract_matching_urls(data):
    """
    Recursively search for and extract URLs matching specific keys ('url' or 'html_url')
    from a nested JSON structure.
    """
    urls = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key in ['html_url', 'url'] and isinstance(value, str):
                urls.append(value)
            else:
                urls.extend(extract_matching_urls(value))
    elif isinstance(data, list):
        for item in data:
            urls.extend(extract_matching_urls(item))

    return urls

def extract_urls(json_file_path, urls_file_path):
    """
    Load the JSON file, recursively extract matching URLs, and save them to a file.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    urls = extract_matching_urls(data)

    with open(urls_file_path, 'w') as file:
        for url in urls:
            file.write(f"{url}\n")

if __name__ == "__main__":
    extract_urls(JSON_FILE_PATH, URLS_FILE_PATH)
    print("URL extraction complete.")