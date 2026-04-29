from nsetools import Nse
import yfinance as yf
import json
from .tickerToName import stockName
import time
import requests

NAME_MAP = stockName()

def mostActive(numberOfStocks=10):
    """
    Fetch most active stocks by volume from NSE API
    Uses local CSV for company names (no external API)
    """

    start_time = time.time()

    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers)
        data = response.json()

        stocks_raw = data.get("data", [])

        # Sort by volume
        sorted_stocks = sorted(
            stocks_raw,
            key=lambda x: float(x.get("totalTradedVolume", 0)),
            reverse=True
        )

        # Remove index entries
        actual_stocks = [
            s for s in sorted_stocks
            if not s.get('symbol', '').startswith('NIFTY')
        ]

        stocks = []

        for stock in actual_stocks[:numberOfStocks]:
            symbol = stock.get('symbol', 'N/A')
            company_name = NAME_MAP.get(symbol, symbol)
            
            # Format change with + or - sign
            change = round(float(stock.get('change', 0)), 2)
            change_str = f"+₹{change}" if change >= 0 else f"-₹{abs(change)}"

            stock_obj = {
                "name": company_name,
                "ticker": symbol,
                "price": round(float(stock.get('lastPrice', 0)), 2),
                "current": change_str,
                "volume": int(float(stock.get('totalTradedVolume', 0))),
                "turnover": float(stock.get('totalTradedValue', 0))
            }

            stocks.append(stock_obj)

        end_time = time.time()

        return {
            "trending_stocks": stocks
        }

    except Exception as e:
        end_time = time.time()
        return {
            "error": str(e),
            "time_taken_seconds": round(end_time - start_time, 3)
        }


# Run locally
# if __name__ == "__main__":
#     result = most_active(20)
#     print(json.dumps(result, indent=2))