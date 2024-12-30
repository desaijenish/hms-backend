from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict
import asyncio
from bs4 import BeautifulSoup
import logging
from cachetools import LRUCache
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt
import json
from fastapi.security.api_key import APIKeyHeader
from schemas.user import AddressRequest, AddressResponse, URlResponse
from util.user_util import (
    fetch_property_details,
    # fetch_with_retry,
    # search_redfin_property,
    process_address,
    process_in_batches,
)
import requests
import aiohttp

# Set up the router and cache

router = APIRouter()
cache = {}  # LRU Cache to store frequently accessed results


# Define the static secret key
STATIC_SECRET_KEY = (
    "UaD2bKcQ3y-Ldf_jp8R6h6P0vTwJlm9MkT1HrGhHk4M"  # Replace with your actual key
)

# Create an API key header dependency
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


# Dependency to validate the secret key
def validate_secret_key(api_key: str = Depends(api_key_header)):
    if api_key != STATIC_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing API Key."
        )


class URLRes(BaseModel):
    id: str
    redfin_url: str


@router.post(
    "/get-redfin-urls/",
    response_model=List[AddressResponse],
    dependencies=[Depends(validate_secret_key)],
)
async def get_redfin_urls(addresses: List[AddressRequest]):
    results = await asyncio.gather(*[process_address(address) for address in addresses])
    return results


# # Single Address API Endpoint
# @router.post(
#     "/get-redfin-url-single/",
#     response_model=AddressResponse,
#     dependencies=[Depends(validate_secret_key)],
# )
# async def get_redfin_url_single(address: AddressRequest):
#     try:
#         full_address = (
#             f"{address.address}, {address.city}, {address.state} {address.zip}"
#         )
#         redfin_url = await search_redfin_property(full_address)

#         if redfin_url == "Not Found":
#             raise HTTPException(status_code=404, detail="Redfin URL not found.")

#         details = await fetch_property_details(redfin_url)
#         return {
#             "id": address.id,
#             "redfin_url": redfin_url,
#             **details,
#         }
#     except Exception as e:
#         logging.error(f"Error processing single address: {e}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


async def fetch_redfin_property(session, full_address: str) -> str:
    """
    Asynchronously fetches the Redfin property URL for a given address.
    """
    formatted_address = full_address.replace(" ", "%20")
    search_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={formatted_address}&v=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        async with session.get(search_url, headers=headers) as response:
            response.raise_for_status()
            raw_text = await response.text()
            prefix = "{}&&"
            if raw_text.startswith(prefix):
                json_text = raw_text[len(prefix) :]
            else:
                json_text = raw_text

            data = json.loads(json_text)

            if data and "payload" in data and "sections" in data["payload"]:
                for section in data["payload"]["sections"]:
                    for item in section["rows"]:
                        if "url" in item:
                            return f"https://www.redfin.com{item['url']}"
        return "Not Found"
    except Exception as e:
        print(f"Error fetching data for address {full_address}: {e}")
        return "Not Found"


async def fetch_all_redfin_urls(addresses: List[AddressRequest]) -> List[dict]:
    """
    Fetch Redfin URLs for a list of addresses asynchronously.
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for entry in addresses:
            # Access attributes using dot notation
            full_address = f"{entry.address}, {entry.city}, {entry.state} {entry.zip}"
            print(f"Fetching URL for: {full_address}")
            tasks.append(fetch_redfin_property(session, full_address))

        results = await asyncio.gather(*tasks)
        return results


@router.post("/get-redfin-urls/web", response_model=List[URlResponse])
async def get_redfin_urls(addresses: List[AddressRequest]):
    """
    Endpoint to get the Redfin URLs for a list of addresses.
    """
    results = await fetch_all_redfin_urls(addresses)
    # Combine the Redfin URLs with their IDs into the response structure
    return [
        {
            "id": entry.id,  # Access the 'id' attribute with dot notation
            "redfin_url": result,
        }
        for entry, result in zip(addresses, results)
    ]


def search_redfin_property(full_address: str) -> str:
    """
    This function takes a full address and queries the Redfin autocomplete API to get the property URL.
    """
    formatted_address = full_address.replace(" ", "%20")
    search_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={formatted_address}&v=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        raw_text = response.text
        prefix = "{}&&"
        if raw_text.startswith(prefix):
            json_text = raw_text[len(prefix) :]
        else:
            json_text = raw_text

        data = json.loads(json_text)

        if data and "payload" in data and "sections" in data["payload"]:
            for section in data["payload"]["sections"]:
                for item in section["rows"]:
                    if "url" in item:
                        return f"https://www.redfin.com{item['url']}"
        return "Not Found"
    except Exception as e:
        print(f"Error fetching data for address {full_address}: {e}")
        return "Not Found"


@router.post("/get-redfin-urls/web/web", response_model=List[URlResponse])
def get_redfin_urls(addresses: List[AddressRequest]):
    """
    Endpoint to get the Redfin URLs for a list of addresses.
    """
    results = []
    for entry in addresses:
        full_address = f"{entry.address}, {entry.city}, {entry.state} {entry.zip}"
        print(f"Fetching URL for: {full_address}")
        redfin_url = search_redfin_property(full_address)
        results.append(
            {
                "id": entry.id,
                "redfin_url": redfin_url,
            }
        )

    return results


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


@router.post(
    "/get-redfin-urls/scraping",
    response_model=List[AddressResponse],
    dependencies=[Depends(validate_secret_key)],
)
async def get_redfin_urls(url: List[URLRes]):

    tasks = [scrape_redfin(i.redfin_url) for i in url]
    results = await asyncio.gather(*tasks)

    response = [
        AddressResponse(
            id=i.id,
            redfin_url=i.redfin_url,
            price=details.get("price", "Not Available"),
            beds=details.get("beds", "Not Available"),
            baths=details.get("baths", "Not Available"),
            sqft=details.get("sqft", "Not Available"),
        )
        for i, details in zip(url, results)
    ]

    return response
