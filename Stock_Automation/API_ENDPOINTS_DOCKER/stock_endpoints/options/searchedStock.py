import yfinance as yf
import json


def searchedStock(stockTicker):
    """
    Fetch stock price and details for a searched stock ticker
    Uses yfinance to get current price and company info
    """

    try:
        ticker = yf.Ticker(stockTicker+".NS")
        info = ticker.info

        stock_data = {
            "stockName" : info.get("longName", "N/A"),
            "stockPrice": info.get("currentPrice", "N/A"),

            "company": {
                "name": info.get("longName", "N/A"),
                "ticker": stockTicker.upper(),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "website": info.get("website", "N/A"),
                "fullTimeEmployees": info.get("fullTimeEmployees", "N/A"),
            },
            "price": {
                "currentPrice": info.get("currentPrice", 0),
                "previousClose": info.get("previousClose", 0),
                "open": info.get("open", 0),
                "dayHigh": info.get("dayHigh", 0),
                "dayLow": info.get("dayLow", 0),
                "currency": info.get("currency", "N/A"),
                "exchange": info.get("fullExchangeName", info.get("exchange", "N/A")),
            },
            "volume": {
                "volume": info.get("volume", 0),
                "averageVolume": info.get("averageVolume", 0),
            },
            "marketStats": {
                "marketCap": info.get("marketCap", 0),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
                "fiftyDayAverage": info.get("fiftyDayAverage", 0),
                "twoHundredDayAverage": info.get("twoHundredDayAverage", 0),
            },
            "valuation": {
                "trailingPE": info.get("trailingPE", "N/A"),
                "forwardPE": info.get("forwardPE", "N/A"),
                "pegRatio": info.get("pegRatio", "N/A"),
                "priceToBook": info.get("priceToBook", "N/A"),
                "epsTrailing": info.get("epsTrailingTwelveMonths", "N/A"),
                "epsForward": info.get("epsForward", "N/A"),
            },
            "dividends": {
                "dividendRate": info.get("dividendRate", 0),
                "dividendYield": info.get("dividendYield", 0),
            },
            "financials": {
                "totalRevenue": info.get("totalRevenue", 0),
                "revenueGrowth": info.get("revenueGrowth", "N/A"),
                "profitMargins": info.get("profitMargins", "N/A"),
                "operatingMargins": info.get("operatingMargins", "N/A"),
                "returnOnEquity": info.get("returnOnEquity", "N/A"),
                "debtToEquity": info.get("debtToEquity", "N/A"),
                "freeCashflow": info.get("freeCashflow", 0),
                "totalCash": info.get("totalCash", 0),
                "totalDebt": info.get("totalDebt", 0),
            },
            "analystRating": {
                "recommendationKey": info.get("recommendationKey", "N/A"),
                "targetMeanPrice": info.get("targetMeanPrice", "N/A"),
                "targetHighPrice": info.get("targetHighPrice", "N/A"),
                "targetLowPrice": info.get("targetLowPrice", "N/A"),
                "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions", 0),
            },
        }

        return stock_data

    except Exception as e:
        return {"error": str(e)}

print(json.dumps(searchedStock("TECHM"), indent=2, default=str))