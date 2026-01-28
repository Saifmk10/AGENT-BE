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
DATA_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/csvFiles"
REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/reports"

# /home/saifmk10/AGENT-SERVICES/AGENT-BE/Stock_Automation/DATA_COLLECTION_DOCKER


#[NOTE] : THIS IS THE PATH USED FOR THE PRODUCTION CODE ONLY AND ONLY FOR DOCKER
# DOCKER_PATH = os.environ.get("DOCKER_PATH")
# DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
# REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


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


    snapshot = {

        "stats":{
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
        },
        "ohlc":{
            "opening" : OHLC_price.iloc[0],
            "high" : OHLC_price.max(),
            "closing" : OHLC_price.iloc[-1],
            "low" : OHLC_price.min(),
        },
        
        
    }
    # print(snapshot)


    return snapshot


# ======> add new features into this once this starts working [MAINLY THE VISUALIZATION] <========


# this function plays the role of the ai parsed message , there is a pre entered prompt that is used within the model where the data from the stock is added into this function to get a parsed user underatable output
ollama_warmed = False # used to check if the ollama has cold start
# def ollamaResponse(data):
#     global ollama_warmed
#     #url = "http://localhost:11434/api/generate" #use for local testing
#     url = "http://ollama:11434/api/generate" #container url works only for docker


#     # runs the code once to prevent cold start
#     if not ollama_warmed:
#         try:
#             requests.post(
#                 url,
#                 json={
#                     "model": "phi3:mini",
#                     "prompt": "OK",
#                     "options": {
#                         "num_predict": 1,
#                         "temperature": 0
#                     },
#                     "stream": False
#                 },
#                 timeout=10
#             )
#         except Exception:
#             pass
#         ollama_warmed = True

#     #prompt used to define the models task \
#     #[NOTE] : update the prompt asper user requirement
#     prompt = f"""
#                 You are analysing stock performance data for a cautious investor.

#                 DATA:
#                 {data}

#                 YOUR GOAL:
#                 Turn the data into clear, practical insights that help a cautious investor understand the stock.

#                 OUTPUT RULES (VERY IMPORTANT):
#                 - Write EXACTLY 4 lines
#                 - Do NOT use HTML
#                 - Do NOT use bullet points or symbols
#                 - Each line MUST start with one of these labels (no other labels allowed):
#                   SUMMARY:
#                   POSITIVE:
#                   NEGATIVE:
#                   DECISION:

#                 CONTENT GUIDELINES:
#                 - SUMMARY:
#                   Describe the recent price behaviour and overall trend.
#                   Length: 20–35 words.

#                 - POSITIVE:
#                   Mention the strongest positive or supportive signal, if any.
#                   Length: 15–30 words.

#                 - NEGATIVE:
#                   Mention the main risk, weakness, or concern.
#                   Length: 15–30 words.

#                 - DECISION:
#                   Write ONLY ONE word — either BUY or AVOID.

#                 DECISION LOGIC:
#                 - If price movement is weak, unclear, sideways, or range-bound → AVOID
#                 - Only write BUY if the movement is clearly directional and stable

#                 CURRENCY RULES:
#                 - You may use ONLY the rupee symbol ₹ and the dollar symbol $
#                 - Do NOT use any other currency symbols

#                 FINAL INSTRUCTION:
#                 Return ONLY the 4 labelled lines.
#                 Do not add explanations, greetings, or extra text.
#                 """

#     # payload used to add all the data and the resouces togther into a small dict so it can be used to send the request
#     payload = {
#         "model": "phi3:mini",
#         "prompt": prompt,
#         "options": {
#             "num_predict": 100,
#             "temperature": 0.2
#         },
#         "stream": False
#     }

#     try:
#         res = requests.post(url, json=payload, timeout=120)
#         text = res.json().get("response", "")

        
#         summary = positive = negative = decision = ""
        
#         # parsing the data obtainer from the ai into sperate categories 
#         for line in text.split("\n"):
#             line = line.strip()
#             if line.startswith("SUMMARY:"):
#                 summary = line.replace("SUMMARY:", "").strip()
#             elif line.startswith("POSITIVE:"):
#                 positive = line.replace("POSITIVE:", "").strip()
#             elif line.startswith("NEGATIVE:"):
#                 negative = line.replace("NEGATIVE:", "").strip()
#             elif line.startswith("DECISION:"):
#                 decision = line.replace("DECISION:", "").strip().upper()

#         #building the html
#         html = []

#         if summary:
#             html.append(f"<p>{summary}</p>")

#         if positive:
#             html.append(f"<p>{positive}</p>")

#         if negative:
#             html.append(f"<p>{negative}</p>")

#         if decision == "BUY":
#             html.append(
#                 "<p style='background-color:#e6f7e6;'><strong>BUY</strong></p>"
#             )
#         else:
#             html.append(
#                 "<p style='background-color:#fdecea;'><strong>AVOID</strong></p>"
#             )

#         return "".join(html)

#     except requests.exceptions.ReadTimeout:
#         return "<p>AI analysis timed out due to system load.</p>"

#     except Exception:
#         return "<p>AI analysis unavailable.</p>"

# function plays a role of validation and authentication , where a map and key is created for each user and the stock that the user has added , this map and key can be used for the stocks authentication
# def usersAndStocksMap():
#     usersAndStocks = {}
#     stockUsers = os.listdir(DATA_DIR)
#     # loop that loops through all the users who has added stock and the data has been colected already , the data is then accessed throught this loop for analysis
#     for users in stockUsers:
#         try:
#             filesAdded = os.path.join("Data_collection_automation","Analysed_Files_data","csvFiles", users)

#             fileContent = os.listdir(filesAdded)     

#             if users not in usersAndStocks:
#                 usersAndStocks[users] = []

#             # content = {users : fileContent}
#             usersAndStocks[users].append(fileContent) # this is the key added to the map here

#         except Exception as error : 
#             print("error in collectedDataAnalysis.py : " , error)

#     return usersAndStocks



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
