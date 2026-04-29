import requests
import json
from .tickerToName import stockName
import time

NAME_MAP = stockName()

def losers(numberOfStocks=10):
    """
    Fetch top losers from NSE API with full company names from CSV
    
    Args:
        numberOfStocks: Number of stocks to return (default 10)
    
    Returns:
        dict with trending_stocks list or error
    """

    start = time.time()

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
        
        # Sort by change (lowest first = losers)
        losers_list = sorted(
            stocks_raw,
            key=lambda x: float(x.get("change", 0)),
            reverse=False
        )
        
        # Remove index entries
        losers_list = [s for s in losers_list if not s.get('symbol', '').startswith('NIFTY')]
        
        stocks = []
        
        for stock in losers_list[:numberOfStocks]:
            try:
                symbol = stock['symbol']
                
                # Get company name from CSV
                company_name = NAME_MAP.get(symbol, symbol)
                
                change = round(float(stock.get('change', 0)), 2)
                change_str = f"-₹{abs(change)}" if change < 0 else f"+₹{change}"
                change_pct = round(float(stock.get('pChange', 0)), 2)
                
                # Build stock object
                stock_obj = {
                    "name": company_name,
                    "ticker": symbol,
                    "price": round(float(stock.get('lastPrice', 0)), 2),
                    "current": change_str,
                    "change_percent": f"{change_pct}%",
                    "volume": int(float(stock.get('totalTradedVolume', 0))),
                    "turnover": float(stock.get('totalTradedValue', 0))
                }
                
                stocks.append(stock_obj)
                
            except Exception as e:
                # Fallback if parsing fails
                stock_obj = {
                    "name": stock.get('symbol', 'N/A'),
                    "ticker": stock.get('symbol', 'N/A'),
                    "price": round(float(stock.get('lastPrice', 0)), 2),
                    "current": f"-₹{abs(round(float(stock.get('change', 0)), 2))}",
                    "change_percent": f"-{round(float(stock.get('pChange', 0)), 2)}%",
                    "volume": int(float(stock.get('totalTradedVolume', 0))),
                    "turnover": float(stock.get('totalTradedValue', 0))
                }
                stocks.append(stock_obj)
        
        end = time.time()
        print(f"Time taken to fetch losers: {round(end - start, 3)} seconds")

        return {"trending_stocks": stocks}
    
    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     result = losers(0)
#     print(json.dumps(result, indent=2))