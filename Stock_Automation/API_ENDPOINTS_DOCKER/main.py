# file that is responsible for making the api be accessable with the help of the fastapi
# these end points will be make public with the help of cloudflare tunnel

from fastapi import FastAPI
from stock_endpoints.options.priceFetcher import stockPriceFetcher
from stock_endpoints.options.searchedStock import SearchedStockPrice
from stock_endpoints.trends.gainers import gainers
from stock_endpoints.trends.looser import looser
from stock_endpoints.trends.mostActive import mostActive

app = FastAPI()

# default api endpoint to test api status
@app.get("/")

def read_root():
    return{"STATUS" : "Api is running"}


# api end point where the users can search for a particular stock   [SEARCH OPTION]
@app.get("/stock/{symbol}")

def get_stock(symbol : str):
    return stockPriceFetcher(symbol) # current api end point being used through the cloudflare is -----> [NOTE] -----> https://stock-api.saifmk.website/stock


@app.get("/search/{symbol}")

def get_search(symbol : str):
    return SearchedStockPrice(symbol)


@app.get("/gainer")

def get_gainer():
    return gainers()


@app.get("/looser")

def get_looser():
    return looser()


@app.get("/mostActive")

def get_mostActive():
    return mostActive()