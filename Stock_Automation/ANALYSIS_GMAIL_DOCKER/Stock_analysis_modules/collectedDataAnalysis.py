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


    stat_report = {
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
    }

    ohlc_report = {
        "opening" : OHLC_price.iloc[0],
        "high" : OHLC_price.max(),
        "closing" : OHLC_price.iloc[-1],
        "low" : OHLC_price.min(),
    }
    


    O = ohlc_report["opening"]
    H = ohlc_report["high"]
    C = ohlc_report["closing"]
    L = ohlc_report["low"]
    R = H - L
    M = stat_report["mean"]
    MED = stat_report["median"]
    Q1 = stat_report["q25"]
    Q3 = stat_report["q75"]
    


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


    snapshot = {

        "stats": stat_report,

        "ohlc": ohlc_report,
        
        "signal": signal_report
    }
    # print(snapshot)


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
