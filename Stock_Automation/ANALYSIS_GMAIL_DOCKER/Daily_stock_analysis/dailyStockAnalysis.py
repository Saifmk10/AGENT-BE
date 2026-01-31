# mail parser plays the role of only sending the mail to an user 

# tasks executed by this module:
# 1.  recives the processed data in the form of a dict from the collectedDataAnalysis.py
# 2.  the data is then added into a report folder that is in the json format , also the data will be added
# 3.  all the stock data is added into the same json under the users email

from datetime import datetime
import time
import os
from datetime import date
import json , requests
from Stock_analysis_modules.collectedDataAnalysis import  fetchCollectedData
from Csv_path_cleaner.cleaningCollectedCsv import cleaningData
# from dotenv import load_dotenv

# [NOTE] docker path used for prod only
DOCKER_PATH = os.environ.get("DOCKER_PATH")
DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


# [NOTE] used for testing 
# DATA_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/csvFiles"
# REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/reports"




# function used to clean the dict data that was generate by the pandas into raw format so it can be added into the json
def jsonFiltering(obj):
    if isinstance(obj, dict):
        return {k: jsonFiltering(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [jsonFiltering(v) for v in obj]
    elif hasattr(obj, "item"): 
        return obj.item()
    return obj





def aiSummary(data):
    start = time.perf_counter()
    url = "http://ollama:11434/api/generate"
    payload = {
        "model": "phi3:mini",
        "prompt": f"""
                    
                    
                    Use OHLC and stats.
                    Breakout: Close>Open and Close=High.
                    Risk: std>1% of mean.
                    Support=q25, Resistance=q75.
                    Trend: Close≥q75 bullish, Close≤q25 bearish.
                    Write a <100-word narrative in rupees.
                    No lists or meta text.


                    {data}
    

                    """,
        "stream": False,
        "tokens" : False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()  # crashes loudly if Ollama is unhappy
    end = time.perf_counter()
    totaltime = end - start
    # print("--------------->" , totaltime)
    print("--------------->", round(totaltime, 3), "seconds")
    return response.json()["response"]





# function used to add the data in json format 
# 1.    access the data from the function for the collectedDataAnalysis.py
# 2.    converts that data into proper raw data like int , string , float so it can be used by json
# 3.    write the data into the report folder in the json format
def JSONconvertor():
    analyzedData = fetchCollectedData()
    Adddate = date.today().strftime("%d-%m-%Y")

    for userEmail, usersData in analyzedData.items():

        user_dir = os.path.join(REPORT_DIR, userEmail)
        os.makedirs(user_dir, exist_ok=True)

        file_name = f"{userEmail}.json"
        file_path = os.path.join(user_dir, file_name)

        # loading the existing data into the code 
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    stored_json = json.load(file)
                    history = stored_json.get("HISTORY", [])
            except json.JSONDecodeError:
                history = []
        else:
            history = []



        # main report dict
        daily_report = {
            "date": Adddate,
            "report": [],
            "summary": ""
        }



        for data in usersData:
            cleaned_stock = jsonFiltering(data)
            daily_report["report"].append(cleaned_stock)

        #  Generate summary for TODAY only
        daily_report["summary"] = aiSummary(daily_report["report"])


        # appending all the data into one dict
        history.append(daily_report)

        # writing the created data into the json file 
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump({"HISTORY": history}, file, indent=2)

            print("DATA WAS ADDED AS JSON FORM SUCCESSFULLY...")

        except OSError as error:
            print("FAILED TO ADD JSON WITH ERROR:", error)


# main fucntion is the entry point for this modlue , where the runDailyAnalysis.py runs this in the docker compose
def main():
    print("RUNNING DAILY STOCK ANALYSIS ...")
    JSONconvertor()
    print("CLEANING DATA FROM THE FOLDER ...")

    try :
        cleaningData() # cleans the csv files so there is no pileup of old data
    except Exception as error:
        print("CLEANING FAILED ERROR :" , error)