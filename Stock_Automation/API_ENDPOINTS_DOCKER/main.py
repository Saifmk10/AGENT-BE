from fastapi import FastAPI
from searchedapi import userSearchedStockPrice

app = FastAPI()

@app.get("/")

def read_root():
    return{"STATUS" : "Api is running"}

@app.get("/stock/{symbol}")

def get_stock(symbol : str):
    return userSearchedStockPrice(symbol)
