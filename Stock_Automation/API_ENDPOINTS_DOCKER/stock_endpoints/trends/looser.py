from nsetools import Nse
import json
from .tickerToName import stockName
import time

NAME_MAP = stockName()
nse = Nse()

def losers(numberOfStocks=10):

    start = time.time()

    try:
        # Get top losers using nsetools
        losers_list = nse.get_top_losers()
        
        # Sort by change percentage (lowest first = losers)
        losers_list = sorted(
            losers_list,
            key=lambda x: float(x.get("perChange", 0)),
            reverse=False
        )
        
        stocks = []
        
        for stock in losers_list[:numberOfStocks]:
            try:
                symbol = stock.get('symbol', stock.get('Symbol', ''))
                
                # Get company name from CSV
                company_name = NAME_MAP.get(symbol, symbol)
                
                # Parse values - handle both string and numeric formats
                change = float(stock.get('net_price', stock.get('change', 0)))
                change = round(change, 2)
                change_str = f"-₹{abs(change)}" if change < 0 else f"+₹{change}"
                
                change_pct = float(stock.get('perChange', stock.get('pChange', 0)))
                change_pct = round(change_pct, 2)
                
                price = float(stock.get('ltp', stock.get('lastPrice', stock.get('Price', 0))))
                price = round(price, 2)
                
                volume = int(float(stock.get('trade_quantity', stock.get('volume', 0))))
                turnover = float(stock.get('turnover', stock.get('value', 0)))
                
                # Build stock object
                stock_obj = {
                    "name": company_name,
                    "ticker": symbol,
                    "price": price,
                    "current": change_str,
                    "change_percent": f"{change_pct}%",
                    "volume": volume,
                    "turnover": turnover
                }
                
                stocks.append(stock_obj)
                
            except Exception as e:
                # Fallback if parsing fails
                symbol = stock.get('symbol', stock.get('Symbol', 'N/A'))
                stock_obj = {
                    "name": symbol,
                    "ticker": symbol,
                    "price": float(stock.get('ltp', stock.get('lastPrice', stock.get('Price', 0)))),
                    "current": f"-₹{abs(round(float(stock.get('net_price', stock.get('change', 0))), 2))}",
                    "change_percent": f"{round(float(stock.get('perChange', stock.get('pChange', 0))), 2)}%",
                    "volume": int(float(stock.get('trade_quantity', stock.get('volume', 0)))),
                    "turnover": float(stock.get('turnover', stock.get('value', 0)))
                }
                stocks.append(stock_obj)
        
        end = time.time()
        print(f"Time taken to fetch losers: {round(end - start, 3)} seconds")

        return {"trending_stocks": stocks}
    
    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     result = losers(10)
#     print(json.dumps(result, indent=2))