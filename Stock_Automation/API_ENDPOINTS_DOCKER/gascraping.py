# this is the file that is responsible for fetching the data from the google analytics , this is done not with an api but with the help of pure web scrapping
# next step is to host this on a backend maybe vercel or hf depending on the cpu usage of the model , 
# currently this is under developement , multiple functions will be needed in order to perfrorm various ops
# this has been hosted as the backend in the vercel from where the api end point id being fetched

import requests
from bs4 import BeautifulSoup
import time
from http.server import BaseHTTPRequestHandler , HTTPServer
import json


# this function is responsible for scrapping the google finance website and fetching a stock price
def niftyPriceFetching() : 
    URL = "https://www.google.com/finance/quote/NIFTY_50:INDEXNSE" #url for fetching price details for the nifty
    response = requests.get(URL)

    # nifty index fetching
    if (response) : 

        try:
            parsedInfo = BeautifulSoup(response.text , "html.parser")

            # fetching the details from the class , if the clas changes in in the google analytics then this needs to be updated
            classNameFromScrapedWeb = "YMlKec fxKbKc"
            finalOutput = float(parsedInfo.find(class_= classNameFromScrapedWeb).text.strip()[0:].replace("," , "")) #here the 0th element is being scrapped , but in the other fetched data the 1st element is stripped just change it as required
            # time.sleep(5)

            return {
                "stockName": "NIFTY 50",
                "stockPrice" : finalOutput, 
                }

            
 
        except Exception as error : 
            return {
                "stockName": "NIFTY 50",
                "stockPrice" : str(error)
                }



# this function is responsible for fetching the sensex data from the realtime google analytics
def senSexPriceFetching() : 
    URL = "https://www.google.com/finance/quote/SENSEX:INDEXBOM" #url for fetching price details for the senSex
    response = requests.get(URL)

    # nifty index fetching
    if (response) : 

        try:
            parsedInfo = BeautifulSoup(response.text , "html.parser")

            # fetching the details from the class , if the clas changes in in the google analytics then this needs to be updated
            classNameFromScrapedWeb = "YMlKec fxKbKc"
            finalOutput = float(parsedInfo.find(class_= classNameFromScrapedWeb).text.strip()[0:].replace("," , "")) #here the 0th element is being scrapped , but in the other fetched data the 1st element is stripped just change it as required
            # time.sleep(5)

            return {
                "stockName": "BSE SENSEX",
                "stockPrice" : finalOutput, 
                }

            
 
        except Exception as error : 
            return {
                "stockName": "NIFTY 50",
                "stockPrice" : str(error)
                }


nseResultFromScrapping = niftyPriceFetching()
bseResultFromScrapping = senSexPriceFetching
combinedResult = {
    "nse" : nseResultFromScrapping,
    "bse" : bseResultFromScrapping,
}


print(combinedResult)
# class handler(BaseHTTPRequestHandler):
 
#     def do_GET(self):
#         try : 
            
#             nseResultFromScrapping = niftyPriceFetching()
#             bseResultFromScrapping = senSexPriceFetching()

#             combinedResult = {
#                 "nse" : nseResultFromScrapping,
#                 "bse" : bseResultFromScrapping,
#             }

#             self.send_response(200)
#             self.send_header('Content-type','application/json')
#             self.end_headers()
#             self.wfile.write(json.dumps(combinedResult).encode('utf-8'))

#         except Exception as error : 
#             self.send_response(500)
#             self.send_header('Content-type','application/json')
#             self.end_headers()
#             self.wfile.write(json.dumps(error).encode('utf-8'))


# used to run the code in local , used for debugging and testing purpose only

# if __name__ == "__main__":
#     # PORT = 8000
#     # server = HTTPServer(("localhost", PORT), handler)
#     # print(f"Local server running at http://localhost:{PORT}")
#     # print("Use curl to test: curl http://localhost:8000")
#     # server.serve_forever()

#     server = handler
#     print(server)