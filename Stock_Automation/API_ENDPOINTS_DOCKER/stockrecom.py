# this end point is responsible for providin the latest trending stock of the day information , it provides both the stock name and the stock price as of now


import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler , HTTPServer
import json 


# function that is responsible for fetching the stock price and the stock name
def recommededStock():
    url = "https://www.google.com/finance"
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

                if name_tag and price_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip().replace("\u20b9" , "") #stock price filtered and raedy to e appended into the list
                    stocks.append({"name": name, "price": price})

            return {"trending_stocks": stocks[:10]}

        except Exception as e:
            return {"error": str(e)}
        


result = recommededStock()
print(result)

# class handler(BaseHTTPRequestHandler):
#     def do_GET(self):

#         try : 
#             recommededStockOutput = recommededStock()

#             result = {
#                 "STOCKS :" : recommededStockOutput
#             }

#             self.send_response(200)
#             self.send_header('Content-type','application/json')
#             self.end_headers()
#             self.wfile.write(json.dumps(result).encode('utf-8'))

#         except Exception as error : 
#             self.send_response(500)
#             self.send_header('Content-type','application/json')
#             self.end_headers()
#             self.wfile.write(json.dumps(error).encode('utf-8'))

# bellow code is used for api testing on the local

# if __name__ == "__main__":
#     PORT = 8000
#     server = HTTPServer(("localhost", PORT), handler)
#     print(f"Local server running at http://localhost:{PORT}")
#     print("Use curl to test: curl http://localhost:8000")
#     server.serve_forever()    