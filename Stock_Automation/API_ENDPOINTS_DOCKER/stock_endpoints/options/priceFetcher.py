#  this api is used internally within the DATA COLLECTION DOCKER where all the data fetching takes place
# uses yfinance for reliable NSE data instead of web scraping
# this api does not handle how the input has been added and will throw error if ticker is not managed properly

import csv
import difflib
import os
import yfinance as yf


CSV_PATH = os.path.join(os.path.dirname(__file__), "EQUITY_L.csv")


def _load_symbols():
    symbols = set()
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)
            for row in reader:
                if row:
                    symbol = row[0].strip().upper()
                    if symbol:
                        symbols.add(symbol)
    except Exception:
        pass
    return symbols


SYMBOLS = _load_symbols()


def _normalize_symbol(raw_symbol):
    normalized = (raw_symbol or "").strip().upper()
    if normalized.endswith(".NS"):
        normalized = normalized[:-3]
    return normalized


def _resolve_symbol(raw_symbol):
    normalized = _normalize_symbol(raw_symbol)
    if not normalized:
        return normalized

    if normalized in SYMBOLS:
        return normalized

    # Handle small input mistakes like REDIGNTON -> REDINGTON.
    close_matches = difflib.get_close_matches(normalized, list(SYMBOLS), n=1, cutoff=0.85)
    return close_matches[0] if close_matches else normalized


def _fetch_ticker_info(symbol):
    ticker = yf.Ticker(f"{symbol}.NS")
    info = ticker.info or {}

    current_price = info.get("currentPrice") or info.get("regularMarketPrice")

    # Fallback for cases where yfinance info is missing/partial.
    if current_price is None:
        history = ticker.history(period="1d", interval="1m")
        if not history.empty and "Close" in history:
            close_series = history["Close"].dropna()
            if not close_series.empty:
                current_price = float(close_series.iloc[-1])

    return ticker, info, current_price


def stockPriceFetcher(stockName):
    try:
        resolved_symbol = _resolve_symbol(stockName)
        ticker, info, currentPrice = _fetch_ticker_info(resolved_symbol)

        # verify we got valid data back
        if currentPrice is None:
            return {
                "stockName": stockName,
                "resolvedTicker": resolved_symbol,
                "stockPrice": "Error: no price data returned from yfinance"
            }

        currentPrice = float(currentPrice)

        currentVolume = info.get("volume") or info.get("regularMarketVolume")
        avgVolume = info.get("averageVolume")
        previousClose = info.get("previousClose") or info.get("regularMarketPreviousClose")
        openPrice = info.get("open") or info.get("regularMarketOpen")
        dayLow = info.get("dayLow") or info.get("regularMarketDayLow")
        dayHigh = info.get("dayHigh") or info.get("regularMarketDayHigh")
        week52Low = info.get("fiftyTwoWeekLow")
        week52High = info.get("fiftyTwoWeekHigh")
        marketCap = info.get("marketCap")
        peRatio = info.get("trailingPE")
        targetPrice = info.get("targetMeanPrice")
        bidValue = info.get("bid")
        askValue = info.get("ask")

        # format market cap as string with suffix for downstream compatibility
        marketCapStr = None
        if marketCap is not None:
            if marketCap >= 1e12:
                marketCapStr = f"{marketCap / 1e12:.3f}T"
            elif marketCap >= 1e9:
                marketCapStr = f"{marketCap / 1e9:.3f}B"
            elif marketCap >= 1e6:
                marketCapStr = f"{marketCap / 1e6:.3f}M"
            else:
                marketCapStr = str(marketCap)

        return {
            "stockName": stockName,
            "resolvedTicker": resolved_symbol,
            "stockPrice": currentPrice,
            "stockVolume": float(currentVolume) if currentVolume is not None else None,
            "stockAvgVolume": float(avgVolume) if avgVolume is not None else None,
            "stockPreviousClosing": float(previousClose) if previousClose is not None else None,
            "stockOpen": float(openPrice) if openPrice is not None else None,
            "stockDayRangeOpening": float(dayLow) if dayLow is not None else None,
            "stockDayRangeClosing": float(dayHigh) if dayHigh is not None else None,
            "stock52WeekRangeOpening": float(week52Low) if week52Low is not None else None,
            "stock52WeekRangeClosing": float(week52High) if week52High is not None else None,
            "stockMarketCap": marketCapStr,
            "stockPERatio": float(peRatio) if peRatio is not None else None,
            "stockTargetPrice": float(targetPrice) if targetPrice is not None else None,
            "stockBid": float(bidValue) if bidValue is not None else None,
            "stockAsk": float(askValue) if askValue is not None else None
        }

    except Exception as error:
        return {
            "stockName": stockName,
            "stockPrice": f"Error: {str(error)}"
        }