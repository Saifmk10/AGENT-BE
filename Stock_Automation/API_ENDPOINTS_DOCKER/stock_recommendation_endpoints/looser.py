# this end point is responsible for providin the latest trending stock of the day information , it provides both the stock name and the stock price as of now


import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler , HTTPServer
import json 


# function that is responsible for fetching the stock price and the stock name
def looser():
    url = "https://www.google.com/finance/markets/losers"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response:
        try:
            soup = BeautifulSoup(response.text, "html.parser")

            # in the google finance website that data of the stock price and the stock name has been added into a ul , so the ul class was fetched to access the inner tags
            stock_list = soup.find("ul", {"class": "sbnBtf"})
            if not stock_list:
                return {"error": "Class not found in end point stockrecom.py"}

            #with the help of the ul class now well be accessing the details from the li tag using the class    
            stocks = []
            for li in stock_list.find_all("li"):
                name_tag = li.find("div", {"class": "ZvmM7"})
                price_tag = li.find("div", {"class": "xVyTdb ytSBif"})

                # fetching the current price like , +90 , -28
                current_price_1 = li.find("div" ,class_="xVyTdb ghTit")
                current_price_2 = current_price_1.find("div" ,  class_="SEGxAb")
                current_price_3 = current_price_2.find("div" , class_="BAftM")
                current_price_4 = current_price_3.find("span" , class_="P2Luy Ez2Ioe")

                # this is the shorter version of the above , this is being used currently above one is as backup
                current_price_tag = li.select_one("div.xVyTdb.ghTit div.SEGxAb div.BAftM span.P2Luy")
    

                if name_tag and price_tag :
                    name = name_tag.text.strip()
                    price = price_tag.text.strip().replace("\u20b9" , "") #stock price filtered and raedy to e appended into the list
                    current_price = current_price_tag.text.strip()
                    stocks.append({"name": name, "price": price , "current" : current_price})

            return {"trending_stocks": stocks[:20]}

        except Exception as e:
            return {"error": str(e)}
        


result = looser()
print(result)
   