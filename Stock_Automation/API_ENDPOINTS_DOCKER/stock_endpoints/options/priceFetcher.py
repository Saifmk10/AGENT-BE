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

        # existing
        priceTag = parsedInfo.find("span", {"data-testid": "qsp-price"})
        volumeTag = parsedInfo.find("fin-streamer", {"data-field": "regularMarketVolume"})
        avgVolumeTag = parsedInfo.find("fin-streamer", {"data-field": "averageVolume"})
        previousClosing = parsedInfo.find("fin-streamer", {"data-field": "regularMarketPreviousClose"})

        # new fields
        openTag = parsedInfo.find("fin-streamer", {"data-field": "regularMarketOpen"})
        dayRangeTag = parsedInfo.find("fin-streamer", {"data-field": "regularMarketDayRange"})
        week52Tag = parsedInfo.find("fin-streamer", {"data-field": "fiftyTwoWeekRange"})
        marketCapTag = parsedInfo.find("fin-streamer", {"data-field": "marketCap"})
        peRatioTag = parsedInfo.find("fin-streamer", {"data-field": "trailingPE"})
        targetPriceTag = parsedInfo.find("fin-streamer", {"data-field": "targetMeanPrice"})

        # bid / ask
        bidLabel = parsedInfo.find("span", {"title": "Bid"})
        askLabel = parsedInfo.find("span", {"title": "Ask"})

        bidTag = bidLabel.find_next("span", class_="value") if bidLabel else None
        askTag = askLabel.find_next("span", class_="value") if askLabel else None


        if priceTag is None:
            return {
                "stockName": stockName,
                "stockPrice": "Error: price element not found"
            }

        # conversions
        currentPrice = float(priceTag.text.replace(",", "").strip())

        currentVolume = float(volumeTag.text.replace(",", "").strip()) if volumeTag else None
        avgVolume = float(avgVolumeTag.text.replace(",", "").strip()) if avgVolumeTag else None
        previousClose = float(previousClosing.text.replace(",", "").strip()) if previousClosing else None

        openPrice = float(openTag.text.replace(",", "").strip()) if openTag else None

        dayRange = dayRangeTag.text.strip() if dayRangeTag else None
        week52Range = week52Tag.text.strip() if week52Tag else None

        marketCap = marketCapTag.text.strip() if marketCapTag else None
        peRatio = float(peRatioTag.text.strip()) if peRatioTag else None
        targetPrice = float(targetPriceTag.text.strip()) if targetPriceTag else None

        bidValue = None if (not bidTag or bidTag.text.strip() in ["--", "-"]) else float(bidTag.text.strip())
        askValue = None if (not askTag or askTag.text.strip() in ["--", "-"]) else float(askTag.text.strip())


        return {
            "stockName": stockName,
            "stockPrice": currentPrice,
            "stockVolume": currentVolume,
            "stockAvgVolume": avgVolume,
            "stockPreviousClosing": previousClose,
            "stockOpen": openPrice,
            "stockDayRange": dayRange,
            "stock52WeekRange": week52Range,
            "stockMarketCap": marketCap,
            "stockPERatio": peRatio,
            "stockTargetPrice": targetPrice,
            "stockBid": bidValue,
            "stockAsk": askValue
        }

    except Exception as error:
        return {
            "stockName": stockName,
            "stockPrice": f"Error: {str(error)}"
        }

# statement = True

# while statement: 
data = stockPriceFetcher("ASHOKLEY")
print(data)