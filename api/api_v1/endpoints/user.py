from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import requests
import json
import time
from sqlalchemy.orm import Session
from api import dependencies
from bs4 import BeautifulSoup
from schemas.user import AddressRequest, AddressResponse, PropertyDetailsResponse
import logging

router = APIRouter()


# def fetch_property_details(url: str) -> dict:
#     """
#     This function takes the Redfin property URL and scrapes the page to get property details.
#     """
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Log the page content to see if the structure changes
#         logging.debug("Page content:\n" + soup.prettify())

#         details = {}

#         # Extracting the price
#         price_section = soup.find("div", {"data-rf-test-id": "abp-price"})
#         if price_section and price_section.find("div", {"class": "statsValue"}):
#             details["price"] = price_section.find("div", {"class": "statsValue"}).text.strip()
#         else:
#             details["price"] = "Not Available"

#         # Extracting the beds
#         beds_section = soup.find("div", {"data-rf-test-id": "abp-beds"})
#         if beds_section and beds_section.find("div", {"class": "statsValue"}):
#             details["beds"] = beds_section.find("div", {"class": "statsValue"}).text.strip()
#         else:
#             details["beds"] = "Not Available"

#         # Extracting the baths
#         baths_section = soup.find("div", {"class": "stat-block baths-section"})
#         if baths_section and baths_section.find("div", {"class": "statsValue"}):
#             details["baths"] = baths_section.find("div", {"class": "statsValue"}).text.strip()
#         else:
#             details["baths"] = "Not Available"

#         # Extracting the square footage
#         sqft_section = soup.find("span", {"class": "statsValue"})
#         if sqft_section:
#             details["sqft"] = sqft_section.text.strip()
#         else:
#             details["sqft"] = "Not Available"

#         return details

#     except Exception as e:
#         logging.error(f"Error fetching data: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


# @router.post("/get-property-details/web", response_model=PropertyDetailsResponse)
# def get_property_details(*, url: str):
#     """
#     Endpoint to get detailed property information from a Redfin URL.
#     """
#     property_details = fetch_property_details(url)
#     return PropertyDetailsResponse(
#         price=property_details["price"],
#         beds=property_details["beds"],
#         baths=property_details["baths"],
#         sqft=property_details["sqft"],
#     )


@router.post("/get-property-details/web", response_model=PropertyDetailsResponse)
def get_property_details(*, url: str):
    """
    Endpoint to get detailed property information from a Redfin URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        # Make the request to fetch the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Log the page content to see if the structure changes
        logging.debug("Page content:\n" + soup.prettify())

        # Initialize a dictionary to store the details
        details = {}

        # Extracting the price
        price_section = soup.find("div", {"data-rf-test-id": "abp-price"})
        if price_section and price_section.find("div", {"class": "statsValue"}):
            details["price"] = price_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["price"] = "Not Available"

        # Extracting the beds
        beds_section = soup.find("div", {"data-rf-test-id": "abp-beds"})
        if beds_section and beds_section.find("div", {"class": "statsValue"}):
            details["beds"] = beds_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["beds"] = "Not Available"

        # Extracting the baths
        print(
            "-------------------------------------------------------------------------",
            details,
        )
        baths_section = soup.find("div", {"class": "stat-block baths-section"})
        if baths_section and baths_section.find("div", {"class": "statsValue"}):
            details["baths"] = baths_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["baths"] = "Not Available"

        # Extracting the square footage
        sqft_section = soup.find("span", {"class": "statsValue"})
        if sqft_section:
            details["sqft"] = sqft_section.text.strip()
        else:
            details["sqft"] = "Not Available"

        # Return the details as response
        return PropertyDetailsResponse(
            price=details["price"],
            beds=details["beds"],
            baths=details["baths"],
            sqft=details["sqft"],
        )

    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


def get_property_details_from_url(url: str):
    """
    Function to get detailed property information from a Redfin URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    try:
        # Make the request to fetch the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Log the page content to see if the structure changes
        logging.debug("Page content:\n" + soup.prettify())

        # Initialize a dictionary to store the details
        details = {}

        # Extracting the price
        price_section = soup.find("div", {"data-rf-test-id": "abp-price"})
        if price_section and price_section.find("div", {"class": "statsValue"}):
            details["price"] = price_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["price"] = "Not Available"

        # Extracting the beds
        beds_section = soup.find("div", {"data-rf-test-id": "abp-beds"})
        if beds_section and beds_section.find("div", {"class": "statsValue"}):
            details["beds"] = beds_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["beds"] = "Not Available"

        # Extracting the baths
        baths_section = soup.find("div", {"class": "stat-block baths-section"})
        if baths_section and baths_section.find("div", {"class": "statsValue"}):
            details["baths"] = baths_section.find(
                "div", {"class": "statsValue"}
            ).text.strip()
        else:
            details["baths"] = "Not Available"

        # Extracting the square footage
        sqft_section = soup.find("span", {"class": "statsValue"})
        if sqft_section:
            details["sqft"] = sqft_section.text.strip()
        else:
            details["sqft"] = "Not Available"

        # Return the details
        return details

    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


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

        try:
            redfin_url = search_redfin_property(full_address)
            if not redfin_url:
                raise HTTPException(
                    status_code=404, detail=f"No Redfin URL found for {full_address}"
                )

            url_data = get_property_details_from_url(redfin_url)

            # Append the property details to the results
            results.append(
                {
                    "id": addresses.id,
                    "redfin_url": redfin_url,
                    "price": url_data["price"],
                    "beds": url_data["beds"],
                    "baths": url_data["baths"],
                    "sqft": url_data["sqft"],
                }
            )
        except Exception as e:
            # Handling any exceptions that occur during URL fetching or property details extraction
            results.append(
                {
                    "id": entry.id,
                    "redfin_url": redfin_url,
                    "price": "Error fetching details",
                    "beds": "Error fetching details",
                    "baths": "Error fetching details",
                    "sqft": "Error fetching details",
                }
            )
            logging.error(f"Error fetching details for {full_address}: {str(e)}")

    return results


@router.post("/get-redfin-url-single/", status_code=200)
def get_redfin_url_single(address_data: AddressRequest):
    """
    Endpoint to get the Redfin URL for a single address object.
    """
    try:
        full_address = f"{address_data.address}, {address_data.city}, {address_data.state} {address_data.zip}"
        print(f"Fetching URL for: {full_address}")

        # Fetch the Redfin URL for the provided address
        redfin_url = search_redfin_property(full_address)

        if not redfin_url:
            raise HTTPException(status_code=404, detail="Redfin URL not found.")

        # Fetch property details from the Redfin URL
        url_data = get_property_details_from_url(redfin_url)

        # Return the property details
        return {
            "id": address_data.id,
            "redfin_url": redfin_url,
            "price": url_data["price"],
            "beds": url_data["beds"],
            "baths": url_data["baths"],
            "sqft": url_data["sqft"],
        }
    except Exception as e:
        # Handle any other errors and log them
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
