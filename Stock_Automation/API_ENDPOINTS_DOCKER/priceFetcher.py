#  this api is used internally within the DATA COLLECTION DOCKER where all the data fetching takes place with the help of this api
# this api does not handle how the input has been added and will throw error is ticker is not managed properly

from http.server import BaseHTTPRequestHandler , HTTPServer
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import json


# fucntion perfromaing the scrapping for the user searched stock
def stockPriceFetcher(stockName):
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



# data = userSearchedStockPrice("ASHOKLEY")
# print(data)