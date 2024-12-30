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
        "https://www.redfin.com/CA/Oakland/2574-63rd-Ave-94605/home/1341788",
  "https://www.redfin.com/CA/Fremont/38770-Blacow-Rd-94536/home/1403761",
  "https://www.redfin.com/CA/San-Leandro/1950-Randy-St-94579/home/1762460",
  "https://www.redfin.com/CA/San-Leandro/337-Dolores-Ave-94577/home/760491",
  "https://www.redfin.com/CA/San-Leandro/850-Melcher-St-94577/home/1645998",
  "https://www.redfin.com/CA/Oakland/487-Hale-Ave-94603/home/1856245",
  "https://www.redfin.com/CA/Oakland/274-Covington-St-94605/home/1995455",
  "https://www.redfin.com/CA/Oakland/7807-Weld-St-94621/home/1277472",
  "https://www.redfin.com/CA/Oakland/1137-76th-Ave-94621/home/1377154",
  "https://www.redfin.com/CA/Hayward/22962-Amador-St-94541/home/40079259",
  "https://www.redfin.com/CA/Oakland/504-Almanza-Dr-94603/home/593111",
  "https://www.redfin.com/CA/Oakland/6221-Buena-Ventura-Ave-94605/home/1509089",
  "https://www.redfin.com/CA/Oakland/2669-67th-Ave-94605/home/571319",
  "https://www.redfin.com/CA/Oakland/7412-Weld-St-94621/home/1001174",
  "https://www.redfin.com/CA/Oakland/9927-Gibraltar-Rd-94603/home/773394",
  "https://www.redfin.com/CA/Oakland/9500-Coral-Rd-94603/home/589333",
  "https://www.redfin.com/CA/Fremont/34194-Gannon-Ter-94555/home/1137406",
  "https://www.redfin.com/CA/Oakland/5808-Chabot-Rd-94618/home/529780",
  "https://www.redfin.com/CA/Fremont/4412-Millard-Ave-94538/home/1107494",
  "https://www.redfin.com/CA/Union-City/34358-Sandburg-Dr-94587/home/1841427",
  "https://www.redfin.com/CA/Union-City/4562-Cabello-St-94587/home/1042196",
  "https://www.redfin.com/CA/Oakland/8115-Dowling-St-94605/home/2000567",
  "https://www.redfin.com/CA/Oakland/2833-Best-Ave-94619/home/1757852",
  "https://www.redfin.com/CA/Berkeley/2620-California-St-94703/home/1458597",
  "https://www.redfin.com/CA/Castro-Valley/20901-Rutledge-Rd-94546/home/1782055",
  "https://www.redfin.com/CA/Oakland/6701-Outlook-Ave-94605/home/772762",
  "https://www.redfin.com/CA/Hayward/27781-Mandarin-Ave-94544/home/1019153",
  "https://www.redfin.com/CA/Hayward/1585-E-St-94541/home/1469312",
  "https://www.redfin.com/CA/Oakland/5520-Picardy-Dr-N-94605/unit-N/home/1422609",
  "https://www.redfin.com/CA/Oakland/1861-66th-Ave-94621/home/570170",
  "https://www.redfin.com/CA/Hayward/3059-Chronicle-Ave-94542/home/17187892",
  "https://www.redfin.com/CA/Oakland/4755-Fairfax-Ave-94601/home/630876",
  "https://www.redfin.com/CA/Alameda/2832-Madison-St-94501/home/1746048",
  "https://www.redfin.com/CA/Oakland/1438-82nd-Ave-94621/home/583068",
  "https://www.redfin.com/CA/Hayward/22646-Woodroe-Ave-94541/home/2008712",
  "https://www.redfin.com/CA/Alameda/742-Haight-Ave-94501/home/1226908",
  "https://www.redfin.com/CA/Emeryville/1060-62nd-St-94608/home/531974",
  "https://www.redfin.com/CA/Fremont/5233-Paxton-Ct-94536/home/1597800",
  "https://www.redfin.com/CA/Oakland/2248-E-22nd-St-94606/home/1957030",
  "https://www.redfin.com/CA/Hayward/848-E-Lewelling-Blvd-94541/home/1723560",
  "https://www.redfin.com/CA/Hayward/532-Ellery-Pl-94544/home/1195818",
  "https://www.redfin.com/CA/Hayward/257-Smalley-Ave-94541/home/1925288",
  "https://www.redfin.com/CA/Oakland/5461-MacArthur-Blvd-94619/home/1517005",
  "https://www.redfin.com/CA/Hayward/31045-Meadowbrook-Ave-94544/home/789332",
  "https://www.redfin.com/CA/Fremont/34447-Colville-Pl-94555/home/745232",
  "https://www.redfin.com/CA/Castro-Valley/5245-Camino-Alta-Mira-94546/home/1513599",
  "https://www.redfin.com/CA/Oakland/2694-74th-Ave-94605/home/574194",
  "https://www.redfin.com/CA/Oakland/6215-Dover-St-94609/home/943098",
  "https://www.redfin.com/CA/Oakland/2546-Parker-Ave-94605/home/1496232",
  "https://www.redfin.com/CA/Union-City/34265-Aspen-Loop-94587/home/698389",
  "https://www.redfin.com/CA/Fremont/35747-Ellmann-Pl-94536/home/1064566",
  "https://www.redfin.com/CA/Hayward/32295-Ithaca-St-94544/home/1367792",
  "https://www.redfin.com/CA/Oakland/9899-Thermal-St-94605/home/711000",
  "https://www.redfin.com/CA/Union-City/32800-Oakdale-Ct-94587/home/1142181",
  "https://www.redfin.com/CA/Newark/6202-Truckee-Ct-94560/home/1543960",
  "https://www.redfin.com/CA/Fremont/459-Washburn-Dr-94536/home/1753206",
  "https://www.redfin.com/CA/Oakland/1146-86th-Ave-94621/home/1118433",
  "https://www.redfin.com/CA/Fremont/36183-Perkins-St-94536/home/1049911",
  "https://www.redfin.com/CA/Hayward/24499-Groom-St-94544/home/996331",
  "https://www.redfin.com/CA/Fremont/35536-Morley-Pl-94536/home/1492299",
  "https://www.redfin.com/CA/Hayward/1122-Gassett-Ct-94544/home/1894552",
  "https://www.redfin.com/CA/Hayward/2603-Perlita-Ct-94541/home/1634396",
  "https://www.redfin.com/CA/Oakland/5623-Bacon-Rd-94619/home/566629",
  "https://www.redfin.com/CA/Oakland/2093-Tunnel-Rd-94611/home/679808",
  "https://www.redfin.com/CA/Oakland/10900-Lochard-St-94605/home/598236",
  "https://www.redfin.com/CA/Oakland/555-El-Paseo-Dr-94603/home/1891905",
  "https://www.redfin.com/CA/Oakland/2841-55th-Ave-94605/home/559051",
  "https://www.redfin.com/CA/Oakland/670-Sycamore-St-94612/home/1328166",
  "https://www.redfin.com/CA/Oakland/9710-Coral-Rd-94603/home/1377273",
  "https://www.redfin.com/CA/San-Lorenzo/1474-Via-Coralla-94580/home/1734610",
  "https://www.redfin.com/CA/Oakland/11222-Monan-St-94605/home/1649809",
  "https://www.redfin.com/CA/Oakland/2016-38th-Ave-94601/home/1803936",
  "https://www.redfin.com/CA/Hayward/1131-Lovelock-Way-94544/home/1570688",
  "https://www.redfin.com/CA/Hayward/27828-Mandarin-Ave-94544/home/1664853",
  "https://www.redfin.com/CA/Hayward/1435-Roosevelt-Ave-94544/home/2011376",
  "https://www.redfin.com/CA/Hayward/2011-Everglade-St-94545/home/1557800",
  "https://www.redfin.com/CA/Hayward/1964-Southgate-St-94545/home/1735764",
  "https://www.redfin.com/CA/San-Lorenzo/1799-Via-Toyon-94580/home/1930593",
  "https://www.redfin.com/CA/Newark/5303-Surrey-Ct-94560/home/859703",
  "https://www.redfin.com/CA/Newark/36916-Olive-St-94560/home/1674895",
  "https://www.redfin.com/CA/Oakland/3069-Malcolm-Ave-94605/home/1564453",
  "https://www.redfin.com/CA/San-Leandro/465-Nabor-St-94578/home/1836574",
  "https://www.redfin.com/CA/Oakland/8426-Aster-Ave-94605/home/1995382",
  "https://www.redfin.com/CA/Oakland/6646-Saroni-Dr-94611/home/1041971",
  "https://www.redfin.com/CA/Oakland/3137-Pleitner-Ave-94602/home/1589282",
  "https://www.redfin.com/CA/Oakland/1066-75th-Ave-94621/home/1937109",
  "https://www.redfin.com/CA/Alameda/1024-Regent-St-94501/home/723020",
  "https://www.redfin.com/CA/San-Lorenzo/1456-Via-Hermana-94580/home/931232",
  "https://www.redfin.com/CA/Hayward/24605-Townsend-Ave-94544/home/990904",
  "https://www.redfin.com/CA/Oakland/2745-Ritchie-St-94605/home/1981530",
  "https://www.redfin.com/CA/San-Leandro/3401-Figueroa-Dr-94578/home/1731585",
  "https://www.redfin.com/CA/Oakland/1107-89th-Ave-94621/home/581427",
  "https://www.redfin.com/CA/Fremont/40481-Davis-St-94538/home/1658376",
  "https://www.redfin.com/CA/Oakland/734-E-24th-St-94606/home/17188226",
  "https://www.redfin.com/CA/Oakland/816-7th-Ave-94606/home/532170",
  "https://www.redfin.com/CA/Oakland/1016-Linden-St-94607/home/1305627",
  "https://www.redfin.com/CA/Oakland/2454-Wilbur-St-94602/home/1477074",
  "https://www.redfin.com/CA/Fremont/33766-Whimbrel-Rd-94555/home/1476359",
  "https://www.redfin.com/CA/Pleasanton/6181-Alvord-Way-94588/home/1302972",
  "https://www.redfin.com/CA/Castro-Valley/5034-Heyer-Ave-94552/home/2046172",
  "https://www.redfin.com/CA/Hayward/26314-Fairview-Ave-94542/home/1892279",
  "https://www.redfin.com/CA/Alameda/1043-Camellia-Dr-94502/home/1927778",
  "https://www.redfin.com/CA/Livermore/1429-Wagoner-Dr-94550/home/1677319",
  "https://www.redfin.com/CA/Oakland/2106-Woodbine-Ave-94602/home/1417210",
  "https://www.redfin.com/CA/Emeryville/5915-San-Pablo-Ave-94608/home/532076",
  "https://www.redfin.com/CA/Castro-Valley/21799-Pheasant-Woods-Dr-94552/home/1995417",
  "https://www.redfin.com/CA/Berkeley/1509-Le-Roy-Ave-94708/home/1673026",
  "https://www.redfin.com/CA/Newark/37152-Aleppo-Dr-94560/home/1222196",
  "https://www.redfin.com/CA/Fremont/233-Kansas-Way-94539/home/1887510",
  "https://www.redfin.com/CA/Pleasanton/1453-Whispering-Oaks-Way-94566/home/2028548",
  "https://www.redfin.com/CA/Hayward/740-Folsom-Ave-94544/home/1570843",
  "https://www.redfin.com/CA/Dublin/5825-Hillbrook-Pl-94568/home/17187099",
  "https://www.redfin.com/CA/Oakland/1606-100th-Ave-94603/home/619042",
  "https://www.redfin.com/CA/Pleasanton/726-Foxbrough-Pl-94566/home/1200054",
  "https://www.redfin.com/CA/Dublin/5811-Southbridge-Way-94568/home/1469160",
  "https://www.redfin.com/CA/Berkeley/1932-Oregon-St-94703/home/925342",
  "https://www.redfin.com/CA/Oakland/6193-Oakdale-Ave-94605/home/564397",
  "https://www.redfin.com/CA/Oakland/6855-Gunn-Dr-94611/home/1745153",
  "https://www.redfin.com/CA/Berkeley/1526-Ashby-Ave-94703/home/1690738",
  "https://www.redfin.com/CA/Hayward/25955-Hickory-Ave-94544/home/2034270",
  "https://www.redfin.com/CA/Hayward/24790-Joe-Mary-Ct-94541/home/651179",
  "https://www.redfin.com/CA/Piedmont/5505-Moraga-Ave-94611/home/1963373",
  "https://www.redfin.com/CA/Oakland/7030-Snake-Rd-94611/home/1937484",
  "https://www.redfin.com/CA/Oakland/881-21st-St-94607/home/524775",
  "https://www.redfin.com/CA/Oakland/964-Village-Cir-94607/home/1442136",
  "https://www.redfin.com/CA/San-Leandro/878-Devonshire-Ave-94579/home/1295017",
  "https://www.redfin.com/CA/Oakland/13650-Skyline-Blvd-94619/home/678847",
  "https://www.redfin.com/CA/Hayward/54-Brookstone-Way-94544/home/738907",
  "https://www.redfin.com/CA/San-Leandro/2404-Lyle-Ct-94578/home/1884496",
  "https://www.redfin.com/CA/Livermore/516-Lorren-Way-94550/home/849957",
  "https://www.redfin.com/CA/Oakland/5724-E-17th-St-94621/home/1243680",
  "https://www.redfin.com/CA/Oakland/251-Rishell-Dr-94619/home/1869953",
  "https://www.redfin.com/CA/Oakland/1170-El-Centro-Ave-94602/home/1496627",
  "https://www.redfin.com/CA/Oakland/8206-Outlook-Ave-94605/home/1189398",
  "https://www.redfin.com/CA/Hayward/1057-Central-Blvd-94542/home/1950839",
  "https://www.redfin.com/CA/Oakland/5467-Crittenden-St-94601/home/554910",
  "https://www.redfin.com/CA/Alameda/1619-Santa-Clara-Ave-94501/home/777126",
  "https://www.redfin.com/CA/San-Leandro/1292-148th-Ave-94578/home/782840",
  "https://www.redfin.com/CA/Oakland/1530-40th-Ave-94601/home/1670899",
  "https://www.redfin.com/CA/Oakland/2439-Havenscourt-Blvd-94605/home/1758065",
  "https://www.redfin.com/CA/Hayward/24742-Broadmore-Ave-94544/home/1920661",
  "https://www.redfin.com/CA/Oakland/3128-Knowland-Ave-94619/home/1118081",
  "https://www.redfin.com/CA/Berkeley/921-Jones-St-94710/home/1414779",
  "https://www.redfin.com/CA/Oakland/4211-Harbor-View-Ave-94619/home/1256507",
  "https://www.redfin.com/CA/Oakland/2523-E-15th-St-94601/home/1524377",
  "https://www.redfin.com/CA/Hayward/2219-Beckham-Way-94541/home/1823230",
  "https://www.redfin.com/CA/Oakland/5500-Laverne-Ave-94605/home/567571",
  "https://www.redfin.com/CA/Oakland/2227-86th-Ave-94605/home/528770",
  "https://www.redfin.com/CA/Hayward/21754-Western-Blvd-94541/home/1896873",
  "https://www.redfin.com/CA/Oakland/4135-Porter-St-94619/home/1925067",
  "https://www.redfin.com/CA/Oakland/2010-45th-Ave-94601/home/2005405",
  "https://www.redfin.com/CA/Oakland/1087-E-33rd-St-94610/home/570965",
  "https://www.redfin.com/CA/Oakland/2830-Sunset-Ave-94601/home/538692",
  "https://www.redfin.com/CA/Oakland/1451-29th-Ave-94601/home/880404",
  "https://www.redfin.com/CA/Fremont/3164-Middlefield-Ave-94539/home/1319212",
  "https://www.redfin.com/CA/Newark/5299-Sussex-Pl-94560/home/1019442",
  "https://www.redfin.com/CA/San-Lorenzo/17367-Via-Rincon-94580/home/937630",
  "https://www.redfin.com/CA/San-Lorenzo/426-Paseo-Grande-94580/home/1614482",
  "https://www.redfin.com/CA/Hayward/170-Hampton-Rd-94541/home/1826569",
  "https://www.redfin.com/CA/Oakland/1145-62nd-Ave-94621/home/1843555",
  "https://www.redfin.com/CA/Oakland/1051-Walker-Ave-94610/home/1726524",
  "https://www.redfin.com/CA/Emeryville/1205-55th-St-94608/home/1913457",
  "https://www.redfin.com/CA/Newark/39832-Potrero-Dr-94560/home/1016514",
  "https://www.redfin.com/CA/Union-City/4352-Victoria-Ave-94587/home/826841",
  "https://www.redfin.com/CA/Oakland/1154-58th-Ave-94621/home/843408",
  "https://www.redfin.com/CA/Alameda/1722-Buena-Vista-Ave-94501/home/1546316",
  "https://www.redfin.com/CA/Oakland/2268-103rd-Ave-94603/home/1118637",
  "https://www.redfin.com/CA/Oakland/3438-Monterey-Blvd-94602/home/1030896",
  "https://www.redfin.com/CA/Hayward/24916-Panitz-St-94541/home/971929",
  "https://www.redfin.com/CA/Fremont/42655-Charleston-Way-94538/home/1117914",
  "https://www.redfin.com/CA/Castro-Valley/3587-Somerset-Ave-94546/home/818882",
  "https://www.redfin.com/CA/Newark/35360-Lake-Blvd-94560/home/1549197",
  "https://www.redfin.com/CA/Hayward/26185-Flamingo-Ave-94544/home/1766700",
  "https://www.redfin.com/CA/Oakland/1720-67th-Ave-94621/home/1141880",
  "https://www.redfin.com/CA/Fremont/1185-Bennett-Ct-94536/home/1512178",
  "https://www.redfin.com/CA/Hayward/3723-Arbutus-Ct-94542/home/971798",
  "https://www.redfin.com/CA/Oakland/684-Nevada-St-94603/home/587730",
  "https://www.redfin.com/CA/Oakland/5401-Leona-St-94619/home/528641",
  "https://www.redfin.com/CA/Oakland/3030-Madeline-St-94602/home/1855748",
  "https://www.redfin.com/CA/Alameda/2525-Eagle-Ave-94501/home/1291194",
  "https://www.redfin.com/CA/Oakland/6962-Saroni-Dr-94611/home/617945",
  "https://www.redfin.com/CA/San-Leandro/1980-Dayton-Ave-94579/home/2019062",
  "https://www.redfin.com/CA/San-Leandro/15090-Edgemoor-St-94579/home/986084",
  "https://www.redfin.com/CA/San-Leandro/1918-Evergreen-Ave-94577/home/1693136",
  "https://www.redfin.com/CA/Oakland/171-Sequoyah-View-Dr-94605/home/1078608",
  "https://www.redfin.com/CA/San-Leandro/531-Sybil-Ave-94577/home/1659033",
  "https://www.redfin.com/CA/San-Leandro/362-Williams-St-94577/home/747361",
  "https://www.redfin.com/CA/Union-City/4053-Horner-St-94587/home/1032550",
  "https://www.redfin.com/CA/Hayward/27030-Parkside-Dr-94542/home/1634471",
  "https://www.redfin.com/CA/Oakland/3911-Edwards-Ave-94605/home/963448",
  "https://www.redfin.com/CA/Newark/5680-Musick-Ave-94560/home/866806",
  "https://www.redfin.com/CA/Fremont/734-Covina-Way-94539/home/1089948",
  "https://www.redfin.com/CA/Hayward/893-Marin-Ave-94541/home/1989817",
  "https://www.redfin.com/CA/Newark/6346-Galletta-Dr-94560/home/863400",
  "https://www.redfin.com/CA/Castro-Valley/21343-Rizzo-Ave-94546/home/1554298",
  "https://www.redfin.com/CA/Oakland/928-Blenheim-St-94603/home/748216",
  "https://www.redfin.com/CA/Berkeley/1433-Hearst-Ave-94702/home/1714193",
  "https://www.redfin.com/CA/Fremont/4254-Ribera-St-94536/home/1133940",
  "https://www.redfin.com/CA/Union-City/1100-Silver-St-94587/home/12114648",
  "https://www.redfin.com/CA/Oakland/6939-MacArthur-Blvd-94605/home/192217668"
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
