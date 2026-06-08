from nsetools import Nse
import json
from .tickerToName import stockName
import time

NAME_MAP = stockName()
nse = Nse()

def gainers(numberOfStocks=10):

    start = time.time()

    try:
        # Get top gainers using nsetools
        gainers_list = nse.get_top_gainers()
        
        # Sort by change percentage (highest first = gainers)
        gainers_list = sorted(
            gainers_list,
            key=lambda x: float(x.get("perChange", 0)),
            reverse=True
        )
        
        stocks = []
        
        for stock in gainers_list[:numberOfStocks]:
            try:
                symbol = stock.get('symbol', stock.get('Symbol', ''))
                
                # Get company name from CSV
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
                turnover = float(stock.get('turnover', stock.get('totalTradedValue', 0)))
                
                # Build stock object
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
                # Fallback if parsing fails
                symbol = stock.get('symbol', stock.get('Symbol', 'N/A'))
                stock_obj = {
                    "name": symbol,
                    "ticker": symbol,
                    "price": float(stock.get('ltp', stock.get('lastPrice', stock.get('Price', 0)))),
                    "current": f"+₹{round(float(stock.get('net_price', stock.get('change', 0))), 2)}",
                    "change_percent": f"+{round(float(stock.get('perChange', stock.get('pChange', 0))), 2)}%",
                    "volume": int(float(stock.get('trade_quantity', stock.get('volume', 0)))),
                    "turnover": float(stock.get('turnover', stock.get('totalTradedValue', 0)))
                }
                stocks.append(stock_obj)
        
        end = time.time()
        print(f"Time taken to fetch gainers: {round(end - start, 3)} seconds")

        return {"trending_stocks": stocks}
    
    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     result = gainers(50)
#     print(json.dumps(result, indent=2))