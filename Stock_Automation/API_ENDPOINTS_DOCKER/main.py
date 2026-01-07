# file that is responsible for making the api be accessable with the help of the fastapi
# these end points will be make public with the help of cloudflare tunnel

from fastapi import FastAPI
from searchedapi import userSearchedStockPrice

app = FastAPI()

# default api endpoint to test api status
@app.get("/")

def read_root():
    return{"STATUS" : "Api is running"}


# api end point where the users can search for a particular stock   [SEARCH OPTION]
@app.get("/stock/{symbol}")

def get_stock(symbol : str):
    return userSearchedStockPrice(symbol)
