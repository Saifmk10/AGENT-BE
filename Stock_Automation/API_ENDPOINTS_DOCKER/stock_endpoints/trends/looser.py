# this end point is responsible for providing the latest trending stock of the day information , it provides both the stock name and the stock price as of now

import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time


# function that is responsible for fetching the stock price and the stock name
def looser(numberOfStocks, timeout=10):
    url = "https://www.google.com/finance/markets/losers"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

            if response:
                soup = BeautifulSoup(response.text, "html.parser")

                # in the google finance website that data of the stock price and the stock name has been added into a ul , so the ul class was fetched to access the inner tags
                stock_list = soup.find("ul", {"class": "sbnBtf"})
                
                # Check if stock_list exists BEFORE trying to use it
                if not stock_list:
                    time.sleep(1)  # Wait 1 second before retrying
                    continue

                # with the help of the ul class now we'll be accessing the details from the li tag using the class    
                stocks = []
                for li in stock_list.find_all("li"):
                    name_tag = li.find("div", {"class": "ZvmM7"})
                    price_tag = li.find("div", {"class": "xVyTdb ytSBif"})

                    # fetching the current price like , +90 , -28
                    current_price_tag = li.select_one("div.xVyTdb.ghTit div.SEGxAb div.BAftM span.P2Luy")
                    if not current_price_tag:
                        current_price_tag = li.select_one("div.xVyTdb.NN5r3b span.NydbP div.JwB6zf")

                    ticker_tag = li.select_one("div.COaKTb")

                    if name_tag and price_tag:
                        name = name_tag.text.strip()
                        price = price_tag.text.strip().replace("\u20b9", "")  # stock price filtered and ready to be appended into the list
                        current_price = current_price_tag.text.strip() if current_price_tag else "N/A"
                        ticker = ticker_tag.text if ticker_tag else None
                        stocks.append({"name": name, "ticker": ticker, "price": price, "current": current_price})
                
                return {"trending_stocks": stocks[:numberOfStocks]}

        except Exception as e:
            return {"error": str(e)}
    
    # Timeout reached
    return {"error": f"Class 'sbnBtf' not found after {timeout} seconds - Google Finance HTML structure may have changed"}


# result = looser(20)
# print(result)