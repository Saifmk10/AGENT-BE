# this file plays the main role for the analysis where the data that is saved in the csv by the data fetching code is analysed
# once this data has been analysed the data is then added into the html format for the mail automation
# the mail automation does not happen from this file and happens in the gmailSubscription.py
# [NOTE] the data collected needs to be analysed again and then segeregated with the help of test conditions 


import csv
import pandas as pd
from pathlib import Path
from google import genai
import os , time
from datetime import datetime
import requests


#[NOTE] : THIS IS THE PATH USED FOR THE LOCAL TESTING ONLY
# DATA_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/csvFiles"
# REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/reports"

# /home/saifmk10/AGENT-SERVICES/AGENT-BE/Stock_Automation/DATA_COLLECTION_DOCKER


#[NOTE] : THIS IS THE PATH USED FOR THE PRODUCTION CODE ONLY AND ONLY FOR DOCKER
DOCKER_PATH = os.environ.get("DOCKER_PATH")
DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


# function that makes sure the folders are created , as the folders are ignored my default 
def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

        

# function reposnsible for the main analysis of that data that has been collected
def analysisPandas (path): 
    
    stockName = path.rsplit("." , 1)[0]

    dataFrame = pd.read_csv(path)
    dataFrame = dataFrame.sort_values("EXTRACTED_TIME")
    OHLC_price = dataFrame["EXTRACTED_PRICE"]


    # contains complete stat of intraday day , all related to the price only 
    stat_report = {
        # price data 
        "count" : dataFrame["EXTRACTED_PRICE"].count(),
        "mean" : dataFrame["EXTRACTED_PRICE"].mean(),
        "median" : dataFrame["EXTRACTED_PRICE"].median(),
        "std" : dataFrame["EXTRACTED_PRICE"].std(),
        "min" : dataFrame["EXTRACTED_PRICE"].min(),
        "max" : dataFrame["EXTRACTED_PRICE"].max(),
        "q25" : dataFrame["EXTRACTED_PRICE"].quantile(0.25),
        "q50" : dataFrame["EXTRACTED_PRICE"].quantile(0.50),
        "q75" : dataFrame["EXTRACTED_PRICE"].quantile(0.75),
        "percentage" : round((dataFrame["EXTRACTED_PRICE"].max() - dataFrame["EXTRACTED_PRICE"].min()) / dataFrame["EXTRACTED_PRICE"].max() * 100 , 2) ,
        "range" : dataFrame["EXTRACTED_PRICE"].max() - dataFrame["EXTRACTED_PRICE"].min(),
        
        # volume data
        "opening_vol" : dataFrame["STOCK_VOLUME"].min(),
        "closing_vol" : dataFrame["STOCK_VOLUME"].max(), 
        "average_vol" : dataFrame["STOCK_VOLUME"].mean(),
    }


    # opening , highest , lowest , closing of intraday report
    ohlc_report = {
        "opening" : OHLC_price.iloc[0],
        "high" : OHLC_price.max(),
        "closing" : OHLC_price.iloc[-1],
        "low" : OHLC_price.min(),
    }


    advanced_report = {
    "stock_open": dataFrame["STOCK_OPEN"].iloc[0],         # Price at market start
    "stock_current": dataFrame["EXTRACTED_PRICE"].iloc[-1],# Most recent price
    "previous_close": dataFrame["STOCK_PREVIOUS_CLOSE"].iloc[0], # Yesterday's final price
    "day_high": dataFrame["STOCK_DAY_RANGE_HIGH"].max(),   # The highest the stock went today
    "day_low": dataFrame["STOCK_DAY_RANGE_LOW"].min(),     # The lowest the stock went today
    "current_volume": dataFrame["STOCK_VOLUME"].iloc[-1],  # Total volume traded so far
    "avg_volume": dataFrame["STOCK_AVG_VOLUME"].iloc[0],   # Normal daily volume
    "target_price": dataFrame["STOCK_TARGET_PRICE"].iloc[0], # Analyst 1-year goal
    "pe_ratio": dataFrame["STOCK_PE_RATIO"].iloc[0],         # Valuation ratio
    "52w_high": dataFrame["STOCK_52_WEEK_HIGH"].max(),       # Yearly resistance level
    "intraday_change_pct": ((dataFrame["EXTRACTED_PRICE"].iloc[-1] - dataFrame["STOCK_OPEN"].iloc[0]) / dataFrame["STOCK_OPEN"].iloc[0]) * 100,
    "rvol": dataFrame["STOCK_VOLUME"].iloc[-1] / dataFrame["STOCK_AVG_VOLUME"].iloc[0]
    }
    

    # these vars are used for creating the signal_report , used to make accessing then easy
    O = ohlc_report["opening"]
    H = ohlc_report["high"]
    C = ohlc_report["closing"]
    L = ohlc_report["low"]
    R = H - L
    M = stat_report["mean"]
    MED = stat_report["median"]
    Q1 = stat_report["q25"]
    Q3 = stat_report["q75"]
    # OV = stat_report["opening_vol"]
    # CV = stat_report["closing_vol"]
    # AV = stat_report["average_vol"]
    #tagetestimate 
    # oneYearEstimate = 0


    # time user for calculation of the volume intensity
    now = datetime.now()
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    minutes_passed = max(1, (now - market_open).seconds // 60)
    total_market_minutes = 375 # 9:15 to 3:30


    curr = advanced_report["stock_current"]
    op = advanced_report["stock_open"]
    pc = advanced_report["previous_close"]
    hi = advanced_report["day_high"]
    lo = advanced_report["day_low"]
    vol = advanced_report["current_volume"]
    avg_v = advanced_report["avg_volume"]
    tp = advanced_report["target_price"]
    hi_52 = advanced_report["52w_high"]


    # predictive_report = {
    #     "intraday_pct_change": 
        
    # }


    
    analysis_metrics = {
    # MOMENTUM: How is the price moving?
    "intraday_pct_change": round(((curr - op) / op) * 100, 2) if op > 0 else 0,
    "overnight_gap_pct": round(((op - pc) / pc) * 100, 2) if pc > 0 else 0,
    "day_range_position": round(((curr - lo) / (hi - lo)) * 100, 2) if hi > lo else 0,

    # CONVICTION: Is the volume supporting the move?
    "rvol": round(vol / avg_v, 2) if avg_v > 0 else 0,
    "volume_intensity": round(vol / (avg_v * (minutes_passed / total_market_minutes)), 2) if avg_v > 0 else 0,

    # VALUATION: Is there room to grow?
    "target_upside_pct": round(((tp - curr) / curr) * 100, 2) if curr > 0 else 0,
    "price_to_52w_high_pct": round(((curr - hi_52) / hi_52) * 100, 2) if hi_52 > 0 else 0,

    # RISK: How "bumpy" is the ride?
    "current_volatility": round(((hi - lo) / curr) * 100, 2) if curr > 0 else 0,
    "valuation_health": "Undervalued" if advanced_report["pe_ratio"] < 20 else "Premium"
}
    



    # creates a boolean report that can be passed into the llm that can help in providing better summary , search online for more info if needed
    signal_report = {
        "VWAP_Hold": C > M,
        "VWAP_Rejection": C < M,
        "Trend_Day_Up": (C > O) and (C >= H - 0.2 * R) if R > 0 else False,
        "Trend_Day_Down": (C < O) and (C <= L + 0.2 * R) if R > 0 else False,
        "Indecision_Day": abs(C - O) < 0.15 * R if R > 0 else False,
        "Late_Buying": C > Q3,
        "Late_Selling": C < Q1,
        "Mid_Range_Close": Q1 <= C <= Q3,
        "Intraday_Strength": (L < O) and (C > MED),
        "Intraday_Weakness": (H > O) and (C < MED),
        "Dip_Absorption": (L < O - 0.5 * R) and (C > MED) if R > 0 else False,
        "Buyer_Control": (C > MED) and (C > O),
        "Seller_Control": (C < MED) and (C < O),
        "Small_Range_Day": (R / M) < 0.006 if M != 0 else False,
        "Wide_Range_Day": (R / M) > 0.015 if M != 0 else False
    }


    # snapshot is the final frame that is retuned , it combines all the dicts above
    snapshot = {

        "stats": stat_report,

        "ohlc": ohlc_report,
        
        "signal": signal_report, 

        "advanced" : advanced_report,
    }
    print(snapshot)


    return snapshot



# this function is used to fetch the csv so it can be passed into the panda for analysis
def fetchCollectedData():

    usersAndStocks = {}
    analyzedData = {}
    stockUsers = os.listdir(DATA_DIR)

    for singleUser in stockUsers:

        analyzedData.setdefault(singleUser, [])

        try :
            #fetching the path where the data has been stored asper the user , for loop loops through all the email ids present 
            path =  os.path.join(DATA_DIR, singleUser)
            stocksAdded = os.listdir(path)
            print("LOOKING AT USER --->" , singleUser)

            # this for loop then moves into the user email folder and fetch the path to all the stocks that has been added so it can use the panda function for analysis
            for stocks in stocksAdded:
                collectedPath =  os.path.join(DATA_DIR, singleUser , stocks)

                #calling the analysis funtions to fetch the data from the analysis 
                snapshot = analysisPandas(collectedPath) # analyzed data that contains the data that has all mean median etc
                
                try : 
                    # this is a dict , where all the users email , stocks they added , that stocks analysis is put into one place
                    # this is done so that each user will get 1 api call for all the stocks reducing cost.
                    # adding the snapshot alone into the ai is enought but then ive added the stock name too , just incase
                    analyzedData[singleUser].append({
                        "stocks" : stocks.split(".")[0],
                        "analysis" : snapshot, 
                    })

                    

                except Exception as error:
                    print("error in dict in collectedDataAnalysis.py:" , error)
           
        except Exception as error:
            print("Error from collectedDataAnalysis.py" , error)

    return analyzedData


data = fetchCollectedData()
print(data)

# def dailyReport():
#     pass
