# file that is responsible for making the api be accessable with the help of the fastapi
# these end points will be make public with the help of cloudflare tunnel

from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from stock_endpoints.options.priceFetcher import stockPriceFetcher
from stock_endpoints.options.searchedStock import searchedStock
from stock_endpoints.trends.gainers import gainers
from stock_endpoints.trends.looser import losers
from stock_endpoints.trends.mostActive import mostActive
from stock_endpoints.news.trendingNews import trendingNews

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # MUST be False with "*"
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# default api endpoint to test api status
@app.get("/")

def read_root():
    return{"STATUS" : "Api is running"}


# api end point where the users can search for a particular stock   [SEARCH OPTION]
@app.get("/stock/{symbol}")
def get_stock(symbol : str):
    return stockPriceFetcher(symbol) # current api end point being used through the cloudflare is -----> [NOTE] -----> https://stock-api.saifmk.online/stock


@app.get("/search/{symbol}")
def get_search(symbol : str):
    return searchedStock(symbol)


@app.get("/gainer")
def get_gainer(limit: int = Query(5, ge=1, le=500)):
    return gainers(limit)


@app.get("/loser")
def get_loser(limit: int = Query(5, ge=1, le=500)):
    return losers(limit)


@app.get("/mostActive")
def get_mostActive(limit: int = Query(5, ge=1, le=500)):
    return mostActive(limit)
# http://127.0.0.1:8000/mostActive?limit=2 format to use 




# news section

@app.get("/trendingNews")
def get_trendingNews(limit : int = Query(5, ge=1, le=200)):
    return trendingNews(limit)


# to run the application manually use [uvicorn main:app --reload]