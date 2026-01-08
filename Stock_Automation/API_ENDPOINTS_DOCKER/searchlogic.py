import json
import csv
import os
from urllib.parse import parse_qs
import requests
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz


# bellow code is for the fuzzy logic , where the code for fetching the data set has been placed so that the dataset is accessed only when called.
def loadTickerList():
    try:
        csvPath = os.path.join(os.path.dirname(__file__), "EQUITY_L.csv")

        ticker = []
        stock = {}

        with open(csvPath, "r", encoding="utf-8") as dataset:
            reader = csv.DictReader(dataset)
            for row in reader:
                symbol = row["SYMBOL"]
                stockName = row["NAME OF COMPANY"]
                ticker.append(symbol)
                stock[symbol] = stockName

        return ticker, stock
    
    except Exception as error: 
        print("CSV ERROR:", repr(error))




# this function is responsible for fuzzy logic where users can search any name and we find closest match
def fuzzyLogic(userSearchedStock, stock):
    userInput = userSearchedStock
    companyNames = list(stock.values())

    result = process.extractOne(userInput, companyNames, scorer=fuzz.WRatio)

    if not result:
        return None

    matchedCompanyName, score, index = result

    if score <= 70:
        return None

    matchedSymbol = list(stock.keys())[index]
    return matchedSymbol



# function that uses the matched ticker and scrapes google finance
def userSearchedStockPrice(stockName):
    tickerList, stockList = loadTickerList()

    stockTicket = fuzzyLogic(stockName, stockList)

    if not stockTicket:
        return {
            "stock": "no matching stock",
            "input stock": stockName
        }

    URL = f"https://www.google.com/finance/quote/{stockTicket}:NSE"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        return {
            "stockName": stockTicket,
            "stockPrice": "Google blocked the request"
        }

    parsedInfo = BeautifulSoup(response.text, "html.parser")
    classNameFromScrapedWeb = "YMlKec fxKbKc"
    priceElement = parsedInfo.find(class_=classNameFromScrapedWeb)

    if not priceElement:
        return {
            "stockName": stockTicket,
            "stockPrice": "Price not found"
        }

    try:
        finalOutput = float(
            priceElement.text.strip()[1:].replace(",", "")
        )
        return {
            "stockName": stockTicket,
            "stockPrice": finalOutput,
        }

    except Exception as error:
        return {
            "stockName": stockTicket,
            "stockPrice": f"Error: {str(error)}"
        }


output = userSearchedStockPrice("Ashok Leyland")
print(output)