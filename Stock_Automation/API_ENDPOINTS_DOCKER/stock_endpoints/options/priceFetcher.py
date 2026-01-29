#  this api is used internally within the DATA COLLECTION DOCKER where all the data fetching takes place with the help of this api
# this api does not handle how the input has been added and will throw error is ticker is not managed properly

from http.server import BaseHTTPRequestHandler , HTTPServer
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import json


# fucntion perfromaing the scrapping for the user searched stock
def stockPriceFetcher(stockName):
    URL = f"https://finance.yahoo.com/quote/{stockName}.NS/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://finance.yahoo.com/"
    }

    response = requests.get(URL, headers=headers, timeout=10)
    print(response)

    if response.status_code != 200:
        return {
            "stockName": stockName,
            "stockPrice": f"HTTP Error {response.status_code}"
        }

    try:
        parsedInfo = BeautifulSoup(response.text, "html.parser")

        # tags used to point to the specific 
        priceTag = parsedInfo.find("span", {"data-testid": "qsp-price"})
        volumeTag = volumeTag = parsedInfo.find( "fin-streamer", {"data-field": "regularMarketVolume"})
        avgVolumeTag = parsedInfo.find("fin-streamer" ,  {"data-field": "averageVolume"})

        if priceTag is None:
            return {
                "stockName": stockName,
                "stockPrice": "Error: price element not found"
            }
        
        # checking if null 
        currentPrice = float(priceTag.text.replace(",", "").strip())

        currentVolume = (
            float(volumeTag.text.replace(",", "").strip())
            if volumeTag else None
        )

        avgVolume = (
            float(avgVolumeTag.text.replace(",", "").strip())
            if avgVolumeTag else None
        )


        return {
            "stockName": stockName,
            "stockPrice": currentPrice,
            "stockVolume": currentVolume,
            "stockAvgVolume": avgVolume
        }

    except Exception as error:
        return {
            "stockName": stockName,
            "stockPrice": f"Error: {str(error)}"
        }

# statement = True

# while statement: 
#     data = stockPriceFetcher("ASHOKLEY")
#     print(data)