import requests
import csv
import json
import time

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

def main():
    # Input list of addresses
    addresses = [
        {"address": "1 Burke", "city": "Irvine", "state": "CA", "zip": "92620"},
        {"address": "10 Kingsport Dr", "city": "Newport Coast", "state": "CA", "zip": "92657"},
        {"address": "100 E 59th St", "city": "Long Beach", "state": "CA", "zip": "90805"},
        {"address": "1000 Corte Primavera", "city": "Oxnard", "state": "CA", "zip": "93030"},
        {"address": "10000 Bevis Ave", "city": "Mission Hills", "state": "CA", "zip": "91345"},
        {"address": "10001 Forbes Ave", "city": "North Hills", "state": "CA", "zip": "91343"},
        {"address": "10001 Mason Ave", "city": "Chatsworth", "state": "CA", "zip": "91311"},
        {"address": "1002 Vale View Dr", "city": "Vista", "state": "CA", "zip": "92081"},
        {"address": "10020 Washington Ave", "city": "South Gate", "state": "CA", "zip": "90280"},
        {"address": "10035 Oso Ave", "city": "Chatsworth", "state": "CA", "zip": "91311"},
        {"address": "10040 Mattock Ave", "city": "Downey", "state": "CA", "zip": "90240"},
        {"address": "1005 S Mountvale Ct", "city": "Anaheim", "state": "CA", "zip": "92808"},
        {"address": "10051 El Capitan Dr", "city": "Huntington Beach", "state": "CA", "zip": "92646"},
        {"address": "10060 Cartagena Dr", "city": "Moreno Valley", "state": "CA", "zip": "92557"},
        {"address": "1007 Flax Ct", "city": "San Diego", "state": "CA", "zip": "92154"},
        {"address": "10070 Quail Ct", "city": "Fountain Valley", "state": "CA", "zip": "92708"},
        {"address": "1009 Del Rio Ave", "city": "Los Angeles", "state": "CA", "zip": "90065"},
        {"address": "1009 E 25th St", "city": "Los Angeles", "state": "CA", "zip": "90011"},
        {"address": "1011 N Whittier St", "city": "Anaheim", "state": "CA", "zip": "92806"}
    ]
   
    # Open CSV file to save results
    with open("redfin_results.csv", mode="w", newline='') as csvfile:
        fieldnames = ["Address", "City", "State", "Zip", "Redfin URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
       
        # Iterate through each address and fetch the Redfin URL
        for entry in addresses:
            full_address = f"{entry['address']}, {entry['city']}, {entry['state']} {entry['zip']}"
            print(f"Fetching URL for: {full_address}")
            redfin_url = search_redfin_property(full_address)
           
            # Write result to CSV
            writer.writerow({
                "Address": entry['address'],
                "City": entry['city'],
                "State": entry['state'],
                "Zip": entry['zip'],
                "Redfin URL": redfin_url if redfin_url else "Not Found"
            })
           
            # Add a short delay to avoid being blocked
            time.sleep(2)

    print("Done! Results saved to 'redfin_results.csv'.")

if __name__ == "__main__":
    main()