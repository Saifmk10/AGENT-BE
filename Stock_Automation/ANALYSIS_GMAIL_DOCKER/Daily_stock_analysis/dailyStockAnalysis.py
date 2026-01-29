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
                    {data}
                    
                    Summarize the following stock-details JSON in under 100 words.
                    Highlight major stocks and important trends only.
                    No bullet points. No extra explanation.
                    Stop immediately once the limit is reached.
                    Keep the currency as rupees
    

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
    # print(analyzedData)
    Adddate = date.today().strftime("%d-%m-%Y")

    for userEmail, usersData in analyzedData.items():
        
        user_dir = os.path.join(REPORT_DIR, userEmail)
        os.makedirs(user_dir, exist_ok=True)

        file_name = f"{userEmail}.json"
        file_path = os.path.join(user_dir, file_name)
        

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    file_data = json.load(file)
            except json.JSONDecodeError:
                file_data = []
        else:
            file_data = []

        for data in usersData: 

            

            cleaned_stock = jsonFiltering(data)
            # cleaned_stock["date"] = Adddate
            file_data.append(cleaned_stock)

        summary = aiSummary(file_data)
        dailyReport = {
            "date" : Adddate,
            "report" : file_data,
            "summary" : summary
        }

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(dailyReport, file, indent=1)

            print("DATA WAS ADDED AS JSON FORM SUCCESSFULLY...")
            # return file_data
            

        except OSError as error:
            print("FAILED TO ADD JSON WITH ERROR :" , error)


# main fucntion is the entry point for this modlue , where the runDailyAnalysis.py runs this in the docker compose
def main():
    print("RUNNING DAILY STOCK ANALYSIS ...")
    JSONconvertor()
