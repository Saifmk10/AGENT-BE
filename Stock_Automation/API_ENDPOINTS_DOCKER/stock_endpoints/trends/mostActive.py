from nsetools import Nse
import json
from .tickerToName import stockName
import time

NAME_MAP = stockName()
nse = Nse()

def mostActive(numberOfStocks=10):
    """
    Fetch most active stocks by volume from NSE using nsetools
    """

    start_time = time.time()

    try:
        # Get top gainers and losers, then filter by volume
        gainers = nse.get_top_gainers()
        losers = nse.get_top_losers()
        
        # Combine and sort by volume
        all_stocks = gainers + losers
        sorted_stocks = sorted(
            all_stocks,
            key=lambda x: float(x.get("trade_quantity", x.get("volume", 0))),
            reverse=True
        )

        stocks = []

        for stock in sorted_stocks[:numberOfStocks]:
            try:
                symbol = stock.get('symbol', stock.get('Symbol', ''))
                company_name = NAME_MAP.get(symbol, symbol)
                
                # Parse values - handle both string and numeric formats
                change = float(stock.get('net_price', stock.get('change', 0)))
                change = round(change, 2)
                change_str = f"+₹{change}" if change >= 0 else f"-₹{abs(change)}"
                
                change_pct = float(stock.get('perChange', stock.get('pChange', 0)))
                change_pct = round(change_pct, 2)
                
                price = float(stock.get('ltp', stock.get('lastPrice', stock.get('Price', 0))))
                price = round(price, 2)
                
                volume = int(float(stock.get('trade_quantity', stock.get('volume', 0))))
                turnover = float(stock.get('turnover', stock.get('value', 0)))
                
                stock_obj = {
                    "name": company_name,
                    "ticker": symbol,
                    "price": price,
                    "current": change_str,
                    "change_percent": f"+{change_pct}%" if change_pct >= 0 else f"{change_pct}%",
                    "volume": volume,
                    "turnover": turnover
                }

                stocks.append(stock_obj)
            except Exception as e:
                continue

        end_time = time.time()

        return {
            "trending_stocks": stocks,
            "time_taken_seconds": round(end_time - start_time, 3)
        }

    except Exception as e:
        end_time = time.time()
        return {
            "error": str(e),
            "time_taken_seconds": round(end_time - start_time, 3)
        }


# Run locally
# if __name__ == "__main__":
#     result = mostActive(20)
#     print(json.dumps(result, indent=2))