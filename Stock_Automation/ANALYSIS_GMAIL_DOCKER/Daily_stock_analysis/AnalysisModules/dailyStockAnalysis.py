# mail parser plays the role of only sending the mail to an user 

# tasks executed by this module:
# 1.  recives the processed data in the form of a dict from the collectedDataAnalysis.py
# 2.  the data is then added into a report folder that is in the json format , also the data will be added
# 3.  all the stock data is added into the same json under the users email

from datetime import datetime
import time
from threading import Lock
import os
from datetime import date
import json , requests
import google.genai as genai
from google.genai import types
from Stock_analysis_modules.collectedDataAnalysis import  fetchCollectedData
from Csv_path_cleaner.cleaningCollectedCsv import cleaningData
from Daily_stock_analysis.DbOperations.intraDayDataToDB import updatingIntrDay
from LLM_API_KEYS import gemini_api_key
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




LAST_GEMINI_CALL = 0
GEMINI_LOCK = Lock()
GEMINI_COOLDOWN = 2.5 


# gemini ai summary , provides the summary for the current day data
# gemini ai summary , provides the summary for the current day data
def aiSummary(data):
    global LAST_GEMINI_CALL

    with GEMINI_LOCK:
        now = time.time()
        remaining = GEMINI_COOLDOWN - (now - LAST_GEMINI_CALL)
        if remaining > 0:
            time.sleep(remaining)
        LAST_GEMINI_CALL = time.time()

    start = time.perf_counter()

    client = genai.Client(api_key=gemini_api_key)

    prompt = f"Analyze: {data}"

    response = client.models.generate_content(
        model="gemini-3-flash-preview",   # IMPORTANT: correct model
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Analyze behavior from JSON. Rules: "
                "Bias: Close>Open? Bullish: Bearish. "
                "Pattern: Close==High? Breakout: Consolidation. "
                "Risk: std>1%mean? High: Low. "
                "Output: Narrative on buyer/seller positioning. "
                "NO numbers/indicators/advice. <80 words total."
            ),
            temperature=0.1,
        )
    )

    # safer response handling
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Empty response from Gemini")

    print(f"Gemini time: {round(time.perf_counter() - start, 3)}s")
    return text.strip()








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
        # try:
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

    try: 
        updatingIntrDay()
    except Exception as error:
        print("FAILED TO WRITE DATA INTO DB :" , error)