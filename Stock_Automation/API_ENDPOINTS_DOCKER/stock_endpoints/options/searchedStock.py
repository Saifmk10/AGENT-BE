import yfinance as yf
import json
import csv
import os
from rapidfuzz import fuzz, process


CSV_PATH = os.path.join(os.path.dirname(__file__), "EQUITY_L.csv")

def load_stock_list():
    """Load stock symbols and names from EQUITY_L.csv"""
    stocks = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) >= 2:
                symbol = row[0].strip()
                name = row[1].strip()
                stocks.append({"symbol": symbol, "name": name})
    return stocks


STOCK_LIST = load_stock_list()
# Separate lookups for symbol and name matching
SYMBOL_LIST = [s["symbol"] for s in STOCK_LIST]
NAME_TO_STOCK = {s["name"].upper(): s for s in STOCK_LIST}
NAME_LIST = list(NAME_TO_STOCK.keys())


def fuzzySearchStock(query, limit=5):
    """
    Fuzzy search for a stock by name or ticker symbol.
    Returns a list of top matches with symbol and match score.
    """
    query = query.strip()
    query_upper = query.upper()

    # Exact symbol match
    for s in STOCK_LIST:
        if s["symbol"].upper() == query_upper:
            return [{"symbol": s["symbol"], "name": s["name"], "score": 100}]

    # Fuzzy match against company names using token_set_ratio
    # (handles partial matches, word reordering, and substring matching well)
    name_results = process.extract(
        query_upper,
        NAME_LIST,
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    # Also match against symbols for partial ticker matches
    symbol_results = process.extract(
        query_upper,
        SYMBOL_LIST,
        scorer=fuzz.WRatio,
        limit=limit
    )

    # Combine and deduplicate results, preferring higher scores
    seen = {}
    for match_name, score, _ in name_results:
        stock = NAME_TO_STOCK[match_name]
        symbol = stock["symbol"]
        if symbol not in seen or score > seen[symbol]["score"]:
            seen[symbol] = {"symbol": symbol, "name": stock["name"], "score": round(score, 2)}

    for match_symbol, score, _ in symbol_results:
        stock = next(s for s in STOCK_LIST if s["symbol"] == match_symbol)
        if match_symbol not in seen or score > seen[match_symbol]["score"]:
            seen[match_symbol] = {"symbol": match_symbol, "name": stock["name"], "score": round(score, 2)}

    # Sort by score descending and return top results
    matches = sorted(seen.values(), key=lambda x: x["score"], reverse=True)[:limit]

    return matches


def searchedStock(stockTicker):
    
    # Fetch stock price and details for a searched stock ticker.
    # Uses fuzzy logic to resolve the ticker from EQUITY_L.csv,
    # then fetches data via yfinance.
    

    try:
        # Resolve ticker using fuzzy search
        matches = fuzzySearchStock(stockTicker)
        if not matches:
            return {"error": "No matching stock found"}

        resolved_symbol = matches[0]["symbol"]

        ticker = yf.Ticker(resolved_symbol + ".NS")
        info = ticker.info

        stock_data = {
            "stockName" : info.get("longName", "Name not found"),
            "stockPrice": info.get("currentPrice", "Price not found"),
            "resolvedTicker": resolved_symbol,
            "fuzzyMatches": matches,

            "company": {
                "name": info.get("longName", "Name not found"),
                "ticker": resolved_symbol,
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "website": info.get("website", "N/A"),
                "fullTimeEmployees": info.get("fullTimeEmployees", "N/A"),
            },
            "price": {
                "currentPrice": info.get("currentPrice", 0),
                "previousClose": info.get("previousClose", 0),
                "open": info.get("open", 0),
                "dayHigh": info.get("dayHigh", 0),
                "dayLow": info.get("dayLow", 0),
                "currency": info.get("currency", "N/A"),
                "exchange": info.get("fullExchangeName", info.get("exchange", "N/A")),
            },
            "volume": {
                "volume": info.get("volume", 0),
                "averageVolume": info.get("averageVolume", 0),
            },
            "marketStats": {
                "marketCap": info.get("marketCap", 0),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
                "fiftyDayAverage": info.get("fiftyDayAverage", 0),
                "twoHundredDayAverage": info.get("twoHundredDayAverage", 0),
            },
            "valuation": {
                "trailingPE": info.get("trailingPE", "N/A"),
                "forwardPE": info.get("forwardPE", "N/A"),
                "pegRatio": info.get("pegRatio", "N/A"),
                "priceToBook": info.get("priceToBook", "N/A"),
                "epsTrailing": info.get("epsTrailingTwelveMonths", "N/A"),
                "epsForward": info.get("epsForward", "N/A"),
            },
            "dividends": {
                "dividendRate": info.get("dividendRate", 0),
                "dividendYield": info.get("dividendYield", 0),
            },
            "financials": {
                "totalRevenue": info.get("totalRevenue", 0),
                "revenueGrowth": info.get("revenueGrowth", "N/A"),
                "profitMargins": info.get("profitMargins", "N/A"),
                "operatingMargins": info.get("operatingMargins", "N/A"),
                "returnOnEquity": info.get("returnOnEquity", "N/A"),
                "debtToEquity": info.get("debtToEquity", "N/A"),
                "freeCashflow": info.get("freeCashflow", 0),
                "totalCash": info.get("totalCash", 0),
                "totalDebt": info.get("totalDebt", 0),
            },
            "analystRating": {
                "recommendationKey": info.get("recommendationKey", "N/A"),
                "targetMeanPrice": info.get("targetMeanPrice", "N/A"),
                "targetHighPrice": info.get("targetHighPrice", "N/A"),
                "targetLowPrice": info.get("targetLowPrice", "N/A"),
                "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions", 0),
            },
        }

        return stock_data

    except Exception as e:
        return {"error": str(e)}

# Test with exact ticker
# print(json.dumps(searchedStock("meesho"), indent=2, default=str))
# Test with fuzzy name search
# print(json.dumps(searchedStock("tech mahindra"), indent=2, default=str))
# print(json.dumps(fuzzySearchStock("reliance"), indent=2, default=str))