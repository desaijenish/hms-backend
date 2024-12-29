from fastapi.requests import Request
from typing import List
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
cache = {} 

def get_current_user(request: Request):
    return request.state.current_user


def get_current_user_permission(request: Request) -> List[str]:
    return request.state.permissions


@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
async def fetch_with_retry(url: str, headers: Dict) -> str:
    """Fetch data from a URL with retry logic."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    
    
async def fetch_property_details(url: str, invalidate_cache: bool = False) -> Dict:
    """
    Fetch property details from the given URL.
    Parameters:
        url (str): The API endpoint.
        invalidate_cache (bool): Whether to ignore the cache and fetch fresh data.
    Returns:
        Dict: Property details or error details.
    """
    # Clear cache if invalidate_cache is True
    if invalidate_cache and url in cache:
        logging.info(f"Invalidating cache for {url}")
        del cache[url]

    # Return cached data if available
    if url in cache:
        logging.info(f"Returning cached data for {url}")
        return cache[url]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    }

    def is_data_available(details):
        """Check if critical data is missing or invalid."""
        invalid_values = ["Not Available", "Error", "", None]
        return not any(value in invalid_values for value in details.values())

    retries = 3  # Number of retries
    while retries > 0:
        try:
            html = await fetch_with_retry(url, headers)
            soup = BeautifulSoup(html, "html.parser")
            details = {}

            # Parse property details
            details["price"] = (
                soup.find("div", {"data-rf-test-id": "abp-price"})
                .find("div", {"class": "statsValue"}).text.strip()
                if soup.find("div", {"data-rf-test-id": "abp-price"})
                else "Not Available"
            )
            details["beds"] = (
                soup.find("div", {"data-rf-test-id": "abp-beds"})
                .find("div", {"class": "statsValue"}).text.strip()
                if soup.find("div", {"data-rf-test-id": "abp-beds"})
                else "Not Available"
            )
            details["baths"] = (
                soup.find("div", {"data-rf-test-id": "abp-baths"})
                .find("div", {"class": "statsValue"}).text.strip()
                if soup.find("div", {"data-rf-test-id": "abp-baths"})
                else "Not Available"
            )
            details["sqft"] = (
                soup.find("div", {"data-rf-test-id": "abp-sqFt"}).text.strip()
                if soup.find("div", {"data-rf-test-id": "abp-sqFt"})
                else "Not Available"
            )

            # Check if all required data is available
            if is_data_available(details):
                cache[url] = details  # Cache the result
                return details
            else:
                logging.warning(f"Incomplete data fetched for {url}: {details}")

        except httpx.RequestError as e:
            logging.error(f"HTTP request error for {url}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error for {url}: {e}")

        # Retry logic
        retries -= 1
        if retries > 0:
            logging.warning(f"Retrying fetch for URL: {url} (remaining retries: {retries})")
            await asyncio.sleep(3)  # Wait before retrying

    # Return error if all retries fail
    logging.error(f"Failed to fetch property details for {url} after retries.")
    return {
        "price": "Error",
        "beds": "Error",
        "baths": "Error",
        "sqft": "Error",
    }

async def search_redfin_property(full_address: str) -> str:
    formatted_address = full_address.replace(" ", "%20")
    search_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={formatted_address}&v=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        html = await fetch_with_retry(search_url, headers)
        raw_text = html
        prefix = "{}&&"
        json_text = raw_text[len(prefix) :] if raw_text.startswith(prefix) else raw_text
        data = json.loads(json_text)

        if data and "payload" in data and "sections" in data["payload"]:
            for section in data["payload"]["sections"]:
                for item in section["rows"]:
                    if "url" in item:
                        return f"https://www.redfin.com{item['url']}"
        return "Not Found"
    except Exception as e:
        logging.error(f"Error searching property: {e}")
        return "Not Found"


# Process address in batches
async def process_in_batches(addresses):
    results = []
    for i in range(0, len(addresses), 50):
        batch = addresses[i : i + 50]
        tasks = [process_address(address) for address in batch]
        results.extend(await asyncio.gather(*tasks))
    return results


# Process a single address
async def process_address(address):
    try:
        full_address = (
            f"{address.address}, {address.city}, {address.state} {address.zip}"
        )
        redfin_url = await search_redfin_property(full_address)

        if redfin_url == "Not Found":
            return {
                "id": address.id,
                "redfin_url": redfin_url,
                "price": "Not Found",
                "beds": "Not Found",
                "baths": "Not Found",
                "sqft": "Not Found",
            }

        details = await fetch_property_details(redfin_url)
        return {
            "id": address.id,
            "redfin_url": redfin_url,
            **details,
        }
    except Exception as e:
        logging.error(f"Error processing address : {e}")
        return {
            "id":'test',
            "redfin_url": "Error",
            "price": "Error",
            "beds": "Error",
            "baths": "Error",
            "sqft": "Error",
        }
