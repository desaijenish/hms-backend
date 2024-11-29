from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Any
from schemas.user import UserDetails, UserOnly, UserCreate, UserInDBBase
from sqlalchemy.orm import Session
from api import dependencies
from sqlalchemy import func
import crud
from util.user_util import get_current_user
import requests
import csv
import json
import time

router = APIRouter()


def search_redfin_property(address):
    """
    This function takes an address and queries the Redfin autocomplete API to get the property URL.
    """
    formatted_address = address.replace(' ', '%20')
    search_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={formatted_address}&v=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
   
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        raw_text = response.text

        # Remove the prefix "{}&&" if present
        prefix = "{}&&"
        if raw_text.startswith(prefix):
            json_text = raw_text[len(prefix):]
        else:
            json_text = raw_text

        # Parse JSON response
        data = json.loads(json_text)
       
        # Check if we have a valid property URL
        if data and 'payload' in data and 'sections' in data['payload']:
            for section in data['payload']['sections']:
                for item in section['rows']:
                    if 'url' in item:
                        return f"https://www.redfin.com{item['url']}"
        return None
    except Exception as e:
        print(f"Error fetching data for address {address}: {e}")
        return None


@router.get("/get-redfin-url/" , status_code=200)
def get_redfin_url(
    *,
    address_request: str,
    db: Session = Depends(dependencies.get_db),
):
    """
    Endpoint to get the Redfin URL for a given address.
    """
    redfin_url = search_redfin_property(address_request)
    if redfin_url:
        return {"address": address_request, "redfin_url": redfin_url}
    else:
        return {"address": address_request, "redfin_url": "Not Found"}


