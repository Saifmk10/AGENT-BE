from http.server import BaseHTTPRequestHandler , HTTPServer
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import json

def userSearchedStockPrice(stockName):
    URL = f"https://www.google.com/finance/quote/{stockName}:NSE"
    response = requests.get(URL)

    if response:
        try:
            parsedInfo = BeautifulSoup(response.text, "html.parser")
            classNameFromScrapedWeb = "YMlKec fxKbKc"
            finalOutput = float(
                parsedInfo.find(class_=classNameFromScrapedWeb)
                .text.strip()[1:]
                .replace(",", "")
            )
            return {
                "stockName": stockName,
                "stockPrice": finalOutput,
            }

        except Exception as error:
            return {
                "stockName": stockName,
                "stockPrice": f"Error: {str(error)}"
            }



data = userSearchedStockPrice("ASHOKLEY")
print(data)