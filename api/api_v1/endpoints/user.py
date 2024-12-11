from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import requests
import json
import time
from sqlalchemy.orm import Session
from api import dependencies

router = APIRouter()


class AddressRequest(BaseModel):
    address: str
    city: str
    state: str
    zip: str


class AddressResponse(BaseModel):
    address: str
    city: str
    state: str
    zip: str
    redfin_url: str


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


@router.post("/get-redfin-urls/", response_model=List[AddressResponse])
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
                "address": entry.address,
                "city": entry.city,
                "state": entry.state,
                "zip": entry.zip,
                "redfin_url": redfin_url,
            }
        )

    return results

@router.post("/get-redfin-url-single/", status_code=200)
def get_redfin_url_single(address_data: AddressRequest):
    """
    Endpoint to get the Redfin URL for a single address object.
    """
    try:
        full_address = f"{address_data.address}, {address_data.city}, {address_data.state} {address_data.zip}"
        print(f"Fetching URL for: {full_address}")
        redfin_url = search_redfin_property(full_address)

        return {
            "address": address_data.address,
            "city": address_data.city,
            "state": address_data.state,
            "zip": address_data.zip,
            "redfin_url": redfin_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")