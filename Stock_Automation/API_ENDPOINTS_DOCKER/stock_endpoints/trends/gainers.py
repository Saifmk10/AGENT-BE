import requests
from bs4 import BeautifulSoup
import time

def gainers(numberOfStocks, timeout=10):
    url = "https://www.google.com/finance/markets/gainers"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

            if response:
                soup = BeautifulSoup(response.text, "html.parser")
                stock_list = soup.find("ul", {"class": "sbnBtf"})
                
                # Check if stock_list exists BEFORE trying to use it
                if not stock_list:
                    time.sleep(1)  # Wait and retry
                    continue
                
                stocks = []
                for li in stock_list.find_all("li"):
                    name_tag = li.find("div", {"class": "ZvmM7"})
                    price_tag = li.find("div", {"class": "xVyTdb ytSBif"})

                    current_price_tag = li.select_one("div.xVyTdb.ghTit div.SEGxAb div.BAftM span.P2Luy")
                    if not current_price_tag:
                        current_price_tag = li.select_one("div.xVyTdb.NN5r3b span.NydbP div.JwB6zf")

                    ticker_tag = li.select_one("div.COaKTb")

                    if name_tag and price_tag:
                        name = name_tag.text.strip()
                        price = price_tag.text.strip().replace("\u20b9", "")
                        current_price = current_price_tag.text.strip() if current_price_tag else "N/A"
                        ticker = ticker_tag.text if ticker_tag else None
                        stocks.append({"name": name, "ticker": ticker, "price": price, "current": current_price})

                return {"trending_stocks": stocks[:numberOfStocks]}

        except Exception as e:
            return {"error": str(e)}
    
    # Timeout reached
    return {"error": f"Class 'sbnBtf' not found after {timeout} seconds - Google Finance HTML structure may have changed"}