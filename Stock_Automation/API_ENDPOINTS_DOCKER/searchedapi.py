from http.server import BaseHTTPRequestHandler , HTTPServer
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import json

def userSearchedStockPrice(stockName):
    URL = f"https://www.google.com/finance/quote/{stockName}:NSE"
    response = requests.get(URL)

    if response:
        try:
            parsedInfo = BeautifulSoup(response.text, "html.parser")
            classNameFromScrapedWeb = "YMlKec fxKbKc"
            finalOutput = float(
                parsedInfo.find(class_=classNameFromScrapedWeb)
                .text.strip()[1:]
                .replace(",", "")
            )
            return {
                "stockName": stockName,
                "stockPrice": finalOutput,
            }

        except Exception as error:
            return {
                "stockName": stockName,
                "stockPrice": f"Error: {str(error)}"
            }

# class handler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         # Parse query parameters
#         query = parse_qs(urlparse(self.path).query)
#         stockName = query.get("symbol", [None])[0]  # e.g. ?symbol=TCS

#         # Validate input
#         if not stockName:
#             self.send_response(400)
#             self.send_header("Content-type", "application/json")
#             self.end_headers()
#             self.wfile.write(json.dumps({"error": "Missing 'symbol' query parameter"}).encode())
#             return

#         # Call your scraper
#         data = userSearchedStockPrice("ASHOKLEY")

#         # Send response
#         self.send_response(200)
#         self.send_header("Content-type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps(data).encode())

# used to run the code in local , used for debugging and testing purpose only

# if __name__ == "__main__":
#     PORT = 8000
#     server = HTTPServer(("localhost", PORT), handler)
#     print(f"Local server running at http://localhost:{PORT}")
#     print("Use curl to test: curl http://localhost:8000")
#     server.serve_forever()

data = userSearchedStockPrice("ASHOKLEY")
print(data)