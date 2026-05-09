#this file is mainly responsible for the fetching of the stocks that he user has added , the stock price along with date and time is fetched here 
#once the fetching is done then it adds that data into a csv in realtime making the data more analysable 
#the data is then analyzed by another file and send via mail

import requests
import time, csv
from zoneinfo import ZoneInfo
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from Data_fetching_from_db.fetching_tokenization import fetchingUserAddedStock
# from DATA_COLLECTION_DOCKER.Data_fetching_from_db.fetching_tokenization import fetchingUserAddedStock


# DATA_DIR = "/home/saifmk10/AGENT-DATA/Stock-Data/TEST/csvFiles"
# DOCKER_PATH = os.environ.get("DOCKER_PATH")
DOCKER_PATH = "/app/Data_collection_automation/Analysed_Files_data"
DATA_DIR = os.path.join(DOCKER_PATH, "csvFiles")

# CSV header - MUST match the analysis code
HEADER = [
    "EXTRACTED_DATE", "EXTRACTED_TIME", "STOCK_NAME", "EXTRACTED_PRICE",
    "STOCK_VOLUME", "STOCK_AVG_VOLUME", "STOCK_PREVIOUS_CLOSE", "STOCK_OPEN",
    "STOCK_DAY_RANGE_LOW", "STOCK_DAY_RANGE_HIGH", "STOCK_52_WEEK_LOW",
    "STOCK_52_WEEK_HIGH", "STOCK_MARKET_CAP", "STOCK_PE_RATIO",
    "STOCK_TARGET_PRICE", "STOCK_BID", "STOCK_ASK"
]

fetchingDBData = fetchingUserAddedStock() # using the data that was fetched form the db , the stocks that has been added by users will be fetched here
stock_to_emails = {}
print("Stocks added and users list", fetchingDBData)

# Create stock to emails mapping
for user in fetchingDBData:
    email = user["email"]
    for stock in user["stocks"]:
        stock_to_emails.setdefault(stock, []).append(email)


# as the api is respoding with 0 as the output for the bid and ask price , so to avoid the problem of having 0 in the csv file we are calculating the bid and ask price from the stock price using a simple formula where we are taking 0.1% of the stock price as the bid ask spread and then calculating the bid and ask price from the stock price
def calculate_bid_ask_from_price(price):
    """
    Calculate BID and ASK when API doesn't provide them
    BID = Price - 0.1% (typical bid-ask spread for liquid stocks)
    ASK = Price + 0.1%
    """
    if price <= 0:
        return 0.0, 0.0

    spread = price * 0.001  # 0.1% spread
    bid = round(price - spread, 2)
    ask = round(price + spread, 2)
    return bid, ask


# checking the api response for the errors and validating the data that is being fetched from the api , this is done to avoid any kind of problem in the future while analyzing the data and also to avoid any kind of problem in the csv file as well
def validate_api_response(data, stock_name):
    """
    Validate API response and check for errors
    Returns: (is_valid, error_message)
    """
    # Check if API returned an error
    if isinstance(data.get("stockPrice"), str) and "Error" in data["stockPrice"]:
        return False, f"API Error: {data['stockPrice']}"

    # Check if critical fields are missing
    critical_fields = ["stockPrice", "stockVolume", "stockAvgVolume"]
    for field in critical_fields:
        if field not in data or data[field] is None:
            return False, f"Missing critical field: {field}"

    # Check if price is 0 or negative
    price = data.get("stockPrice")
    if isinstance(price, (int, float)) and price <= 0:
        return False, f"Invalid price: {price}"

    return True, "OK"


def extract_and_clean_data(data, stock_name):
    """
    Extract data from API response and clean/validate it
    Returns: dict with all stock data fields
    """

    # CRITICAL FIELDS - must have valid data
    try:
        price = float(data.get("stockPrice", 0))
        if price <= 0:
            raise ValueError(f"Invalid price: {price}")
    except (ValueError, TypeError):
        print(f"❌ {stock_name}: Invalid price, skipping")
        return None

    # STANDARD FIELDS - use 0 if missing
    volume = float(data.get("stockVolume")) if data.get("stockVolume") is not None else 0.0
    avg_vol = float(data.get("stockAvgVolume")) if data.get("stockAvgVolume") is not None else 0.0
    prev_close = float(data.get("stockPreviousClosing")) if data.get("stockPreviousClosing") is not None else 0.0
    open_price = float(data.get("stockOpen")) if data.get("stockOpen") is not None else 0.0
    day_low = float(data.get("stockDayRangeOpening")) if data.get("stockDayRangeOpening") is not None else 0.0
    day_high = float(data.get("stockDayRangeClosing")) if data.get("stockDayRangeClosing") is not None else 0.0
    week_52_low = float(data.get("stock52WeekRangeOpening")) if data.get("stock52WeekRangeOpening") is not None else 0.0
    week_52_high = float(data.get("stock52WeekRangeClosing")) if data.get("stock52WeekRangeClosing") is not None else 0.0

    # OPTIONAL FIELDS with special handling
    # market cap can come as a string like "159.188B" , "1.5T" , "500M" , "100K" so we need to strip the suffix and convert to float
    marketCapRaw = str(data.get("stockMarketCap", "0") or "0").strip().upper()
    marketCapSuffixes = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
    if marketCapRaw and marketCapRaw[-1] in marketCapSuffixes:
        market_cap = float(marketCapRaw[:-1]) * marketCapSuffixes[marketCapRaw[-1]]
    else:
        market_cap = float(marketCapRaw) if marketCapRaw else 0.0


    pe_ratio = float(data.get("stockPERatio")) if data.get("stockPERatio") is not None else 0.0
    target_price = float(data.get("stockTargetPrice")) if data.get("stockTargetPrice") is not None else 0.0

    #PROBLEM: Your API doesn't provide BID/ASK - calculate them instead
    bid = float(data.get("stockBid")) if data.get("stockBid") is not None else None
    ask = float(data.get("stockAsk")) if data.get("stockAsk") is not None else None

    # If BID/ASK are missing or 0, calculate them from price
    if bid is None or bid == 0 or ask is None or ask == 0:
        bid, ask = calculate_bid_ask_from_price(price)
        bid_ask_source = "CALCULATED"
    else:
        bid_ask_source = "API"

    return {
        "name": stock_name,
        "price": price,
        "volume": volume,
        "avg_vol": avg_vol,
        "prev_close": prev_close,
        "open_price": open_price,
        "day_low": day_low,
        "day_high": day_high,
        "week_52_low": week_52_low,
        "week_52_high": week_52_high,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "target_price": target_price,
        "bid": bid,
        "ask": ask,
        "bid_ask_source": bid_ask_source,
    }


def save_to_csv(stock_data, email, date, current_time):
    """
    Save stock data to CSV file for the given email
    Creates user directory and file if they don't exist
    """
    try:
        # Create user directory
        csv_dir = os.path.join(DATA_DIR, email)
        os.makedirs(csv_dir, exist_ok=True)

        # Create file path
        file_path = os.path.join(csv_dir, f"{stock_data['name']}.csv")

        # Check if file exists (to determine if we need to write header)
        file_exists = os.path.isfile(file_path)

        # Write to CSV
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)

            # Write header if file is new
            if not file_exists:
                writer.writerow(HEADER)

            # Write data row
            writer.writerow([
                date, current_time, stock_data["name"],
                stock_data["price"],
                stock_data["volume"], stock_data["avg_vol"],
                stock_data["prev_close"], stock_data["open_price"],
                stock_data["day_low"], stock_data["day_high"],
                stock_data["week_52_low"], stock_data["week_52_high"],
                stock_data["market_cap"], stock_data["pe_ratio"],
                stock_data["target_price"], stock_data["bid"],
                stock_data["ask"]
            ])

        return True, "OK"

    except Exception as error:
        return False, str(error)


def log_data_quality(stock_data):
    """
    Log data quality status for monitoring
    Helps identify which API fields are missing
    """
    issues = []

    if stock_data["pe_ratio"] == 0:
        issues.append("P/E Ratio missing from API")

    if stock_data["bid_ask_source"] == "CALCULATED":
        issues.append("BID/ASK calculated (not from API)")

    if stock_data["target_price"] == 0:
        issues.append("Target Price missing from API")

    if issues:
        print(f"{stock_data['name']} - Data Quality: {', '.join(issues)}")
    else:
        print(f"{stock_data['name']} - All fields available")


# this function plays the main role where the data (stock price) is collected on a loop and saved in a csv file for the other modules to analyze later
def priceFetcher(stockName):
    """
    Main fetcher function - continuously fetches stock data and saves to CSV
    Runs in its own thread for each stock
    """

    # url = f"https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol={stockName}"
    url = f"https://stock-api.saifmk.online/stock/{stockName}"

    MARKET_OPEN = datetime.strptime("09:15:00", "%H:%M:%S").time() # NSE market open
    MARKET_CLOSE = datetime.strptime("15:30:00", "%H:%M:%S").time() # NSE market close
    last_saved_time = None # tracks last written timestamp to prevent duplicates

    while True:
        try:
            # Get current date and time in IST
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            date = now.strftime("%d-%m-%Y")
            current_time = now.strftime("%H:%M:%S")

            # skip fetch if outside market hours
            if not (MARKET_OPEN <= now.time() <= MARKET_CLOSE):
                print(f"Outside market hours ({current_time} IST), skipping {stockName}")
                time.sleep(60) # check again in 1 min
                continue

            # api calling
            print(f"\nFetching {stockName} at {current_time}")
            response = requests.get(url, timeout=10)
            print(f"Response Status: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            # ==================== VALIDATION ====================
            is_valid, validation_msg = validate_api_response(data, stockName)
            if not is_valid:
                print(f" Validation Failed: {validation_msg}")
                time.sleep(2)
                continue

            # ==================== DATA EXTRACTION ====================
            # these collect the exact data that has been generated from the json repsonse and then added into the csv
            stock_data = extract_and_clean_data(data, stockName)
            if stock_data is None:
                time.sleep(2)
                continue

            # Log data quality
            log_data_quality(stock_data)

            # skip if this timestamp was already saved (prevents duplicates on retry)
            if current_time == last_saved_time:
                print(f"Duplicate timestamp {current_time} for {stockName}, skipping")
                time.sleep(300)
                continue
            last_saved_time = current_time

            # ==================== SAVE TO CSV ====================
            # using the key value pair mentioned above to add the data into the respective path
            # for each user a new folder will be created in his/her email id so segregation is simple and can avoid any kind of mix ups while sending the mail
            for email in stock_to_emails.get(stockName, []):
                success, msg = save_to_csv(stock_data, email, date, current_time)

                if success:
                    print(f"Saved for --------> {email}")
                else:
                    print(f"FAILED to save for --------> {email}: {msg}")

            # Wait before next fetch (5 minutes = 300 seconds)
            time.sleep(300)  #[NOTE]change to 300 in prod =================<>=======================

        except KeyboardInterrupt:
            # raise
            print("KEYBOARD INTERRUPTION...") # only happens in the test , not in the container

        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code
            print(f"HTTP Error {status_code}")

            if status_code in (404, 403, 429): # will re run the try block
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
                continue
            else:
                print("FETCHING FAILED DUE TO HTTP CODE :", error)
                break

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            print("NETWORK ERROR, RETRYING:", error)
            time.sleep(2)
            continue

        except Exception as error:
            print("THREAD CRASHED WITH :", repr(error))
            time.sleep(2)
            continue


# main function is the runnnig function this is executed with the help of the run.py function, done to prevent the modules and folder conflicts
def main():
    """
    Main entry point - starts threading for all stocks
    """
    jobs = set() # here the jobs are the stock name that is being fetched from the users who has the subscription

    for user in fetchingDBData:
        stockNames = user["stocks"]

        if not stockNames:
            continue

        for stock in stockNames:
            jobs.add(stock)

    if not jobs:
        print("❌ No stocks to fetch")
        return

    print(f"\n{'='*60}")
    print(f"Starting fetcher for {len(jobs)} stocks")
    print(f"Stocks: {', '.join(sorted(jobs))}")
    print(f"{'='*60}\n")

    try:
        # Create thread pool with one thread per stock
        with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
            executor.map(priceFetcher, jobs)
    except KeyboardInterrupt:
        print("FETCHING STOCK STOPPED BY KEYBOARD..")

# main()