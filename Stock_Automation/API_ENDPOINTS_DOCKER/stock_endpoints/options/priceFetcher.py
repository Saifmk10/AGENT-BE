#  this api is used internally within the DATA COLLECTION DOCKER where all the data fetching takes place
# uses yfinance for reliable NSE data instead of web scraping
# this api does not handle how the input has been added and will throw error if ticker is not managed properly

import yfinance as yf


def stockPriceFetcher(stockName):
    try:
        ticker = yf.Ticker(f"{stockName}.NS")
        info = ticker.info

        # verify we got valid data back
        currentPrice = info.get("currentPrice") or info.get("regularMarketPrice")
        if currentPrice is None:
            return {
                "stockName": stockName,
                "stockPrice": "Error: no price data returned from yfinance"
            }

        currentPrice = float(currentPrice)

        currentVolume = info.get("volume") or info.get("regularMarketVolume")
        avgVolume = info.get("averageVolume")
        previousClose = info.get("previousClose") or info.get("regularMarketPreviousClose")
        openPrice = info.get("open") or info.get("regularMarketOpen")
        dayLow = info.get("dayLow") or info.get("regularMarketDayLow")
        dayHigh = info.get("dayHigh") or info.get("regularMarketDayHigh")
        week52Low = info.get("fiftyTwoWeekLow")
        week52High = info.get("fiftyTwoWeekHigh")
        marketCap = info.get("marketCap")
        peRatio = info.get("trailingPE")
        targetPrice = info.get("targetMeanPrice")
        bidValue = info.get("bid")
        askValue = info.get("ask")

        # format market cap as string with suffix for downstream compatibility
        marketCapStr = None
        if marketCap is not None:
            if marketCap >= 1e12:
                marketCapStr = f"{marketCap / 1e12:.3f}T"
            elif marketCap >= 1e9:
                marketCapStr = f"{marketCap / 1e9:.3f}B"
            elif marketCap >= 1e6:
                marketCapStr = f"{marketCap / 1e6:.3f}M"
            else:
                marketCapStr = str(marketCap)

        return {
            "stockName": stockName,
            "stockPrice": currentPrice,
            "stockVolume": float(currentVolume) if currentVolume is not None else None,
            "stockAvgVolume": float(avgVolume) if avgVolume is not None else None,
            "stockPreviousClosing": float(previousClose) if previousClose is not None else None,
            "stockOpen": float(openPrice) if openPrice is not None else None,
            "stockDayRangeOpening": float(dayLow) if dayLow is not None else None,
            "stockDayRangeClosing": float(dayHigh) if dayHigh is not None else None,
            "stock52WeekRangeOpening": float(week52Low) if week52Low is not None else None,
            "stock52WeekRangeClosing": float(week52High) if week52High is not None else None,
            "stockMarketCap": marketCapStr,
            "stockPERatio": float(peRatio) if peRatio is not None else None,
            "stockTargetPrice": float(targetPrice) if targetPrice is not None else None,
            "stockBid": float(bidValue) if bidValue is not None else None,
            "stockAsk": float(askValue) if askValue is not None else None
        }

    except Exception as error:
        return {
            "stockName": stockName,
            "stockPrice": f"Error: {str(error)}"
        }