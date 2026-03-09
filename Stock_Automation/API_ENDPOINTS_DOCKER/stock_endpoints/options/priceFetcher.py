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
        bidTag = parsedInfo.find("fin-streamer", {"data-field": "bid"})
        askTag = parsedInfo.find("fin-streamer", {"data-field": "ask"})

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
        dayRangeOpening = float(dayRange.split(" - ")[0].replace(",", "")) if dayRange else None
        dayRangeClosing = float(dayRange.split(" - ")[1].replace(",", "")) if dayRange else None


        week52Range = week52Tag.text.strip() if week52Tag else None
        week52Opening = float(week52Range.split(" - ")[0].replace(",", "")) if week52Range else None
        week52Closing = float(week52Range.split(" - ")[1].replace(",", "")) if week52Range else None



        marketCap = str(marketCapTag.text.strip().replace(",", "")) if marketCapTag else None # was getting an alpahbets here , so using the strip
        peRatio = float(peRatioTag.text.replace(",", "").strip()) if peRatioTag and peRatioTag.text.strip() not in ('N/A', '--', '-') else None
        targetPrice = float(targetPriceTag.text.replace(",", "").strip()) if targetPriceTag and targetPriceTag.text.strip() not in ('N/A', '--', '-') else None

        bidValue = None
        if bidTag and 'x' in bidTag.text:
            bid_price_str = bidTag.text.split('x')[0].strip().replace(',', '')
            if bid_price_str not in ["--", "-"]:
                bidValue = float(bid_price_str)
        askValue = None
        if askTag and 'x' in askTag.text:
            ask_price_str = askTag.text.split('x')[0].strip().replace(',', '')
            if ask_price_str not in ["--", "-"]:
                askValue = float(ask_price_str)


        return {
            "stockName": stockName,
            "stockPrice": currentPrice,
            "stockVolume": currentVolume,
            "stockAvgVolume": avgVolume,
            "stockPreviousClosing": previousClose,
            "stockOpen": openPrice,
            # "stockDayRange": dayRange,
            "stockDayRangeOpening": dayRangeOpening,
            "stockDayRangeClosing": dayRangeClosing,
            # "stock52WeekRange": week52Range,
            "stock52WeekRangeOpening": week52Opening,
            "stock52WeekRangeClosing": week52Closing,
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


# data = stockPriceFetcher("ASHOKLEY")
# print(data)