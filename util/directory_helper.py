import requests
from bs4 import BeautifulSoup
import time
import random
import os
import uuid
import aiohttp
import asyncio

def create_directory(base_directory, category_id, sub_category_id):
    folder_path = os.path.join(base_directory, str(category_id), str(sub_category_id))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def create_document_directory(base_directory, name):
    folder_path = os.path.join(base_directory, str(name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def generate_file_name(extension):
    return f"{uuid.uuid4()}.png"

async def fetch_with_retry(url, headers, retries=3):
    """Fetch URL with retries."""
    while retries > 0:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 202:
                        print(f"Received 202 from {url}. Retrying...")
                    else:
                        print(f"Error: {response.status} from {url}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        retries -= 1
        await asyncio.sleep(5)  # Increase delay for retries
    return None

async def scrape_redfin(url):
    """Scrape Redfin property details."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    html = await fetch_with_retry(url, headers)
    if not html:
        print(f"Failed to fetch {url}")
        return {
            "url": url,
            "price": "Error",
            "beds": "Error",
            "baths": "Error",
            "sqft": "Error",
        }

    soup = BeautifulSoup(html, "html.parser")
    details = {}

    # Extract details with fallback
    details["price"] = (
        soup.find("div", {"data-rf-test-id": "abp-price"})
        .find("div", {"class": "statsValue"})
        .text.strip()
        if soup.find("div", {"data-rf-test-id": "abp-price"})
        else "Not Available"
    )
    details["beds"] = (
        soup.find("div", {"data-rf-test-id": "abp-beds"})
        .find("div", {"class": "statsValue"})
        .text.strip()
        if soup.find("div", {"data-rf-test-id": "abp-beds"})
        else "Not Available"
    )
    details["baths"] = (
        soup.find("div", {"data-rf-test-id": "abp-baths"})
        .find("div", {"class": "statsValue"})
        .text.strip()
        if soup.find("div", {"data-rf-test-id": "abp-baths"})
        else "Not Available"
    )
    details["sqft"] = (
        soup.find("div", {"data-rf-test-id": "abp-sqFt"}).text.strip()
        if soup.find("div", {"data-rf-test-id": "abp-sqFt"})
        else "Not Available"
    )

    details["url"] = url
    return details

async def main():
    # Example list of URLs to scrape
    urls = [
        "https://www.redfin.com/CA/Irvine/1-Burke-92620/home/4783358",
        "https://www.redfin.com/CA/Long-Beach/100-E-59th-St-90805/home/7513073",
        "https://www.redfin.com/CA/Oxnard/1000-Corte-Primavera-93030/home/4533899",
        "https://www.redfin.com/CA/Mission-Hills/10000-Bevis-Ave-91345/home/5660106",
        "https://www.redfin.com/CA/North-Hills/10001-Forbes-Ave-91343/home/5738534",
        # Add more URLs here
    ]

    tasks = [scrape_redfin(url) for url in urls]
    results = await asyncio.gather(*tasks)

    print("\nScraped Data:")
    for result in results:
        print(result)

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
