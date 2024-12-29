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
from schemas.user import AddressRequest, AddressResponse ,URlResponse
from util.user_util import (
    fetch_property_details,
    fetch_with_retry,
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


# @router.post(
#     "/get-redfin-urls/web",
#     response_model=List[URLRes],
#     dependencies=[Depends(validate_secret_key)],
# )
# async def get_redfin_urls(addresses: List[AddressRequest]):
#     full_address = (
#         f"{addresses.address}, {addresses.city}, {addresses.state} {addresses.zip}"
#     )
#     formatted_address = full_address.replace(" ", "%20")
#     search_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={formatted_address}&v=2"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
#     }

#     try:
#         html = await fetch_with_retry(search_url, headers)
#         raw_text = html
#         prefix = "{}&&"
#         json_text = raw_text[len(prefix) :] if raw_text.startswith(prefix) else raw_text
#         data = json.loads(json_text)

#         if data and "payload" in data and "sections" in data["payload"]:
#             for section in data["payload"]["sections"]:
#                 for item in section["rows"]:
#                     if "url" in item:
#                         return f"https://www.redfin.com{item['url']}"
#         return "Not Found"
#     except Exception as e:
#         logging.error(f"Error searching property: {e}")
#         return "Not Found"
#     return results


@router.post(
    "/get-redfin-urls/scraping",
    response_model=List[AddressResponse],
    dependencies=[Depends(validate_secret_key)],
)
async def get_redfin_urls(url: List[URLRes]):
    results = await asyncio.gather(*[fetch_property_details(i.redfin_url) for i in url])

    # Create a response with the additional fields
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
