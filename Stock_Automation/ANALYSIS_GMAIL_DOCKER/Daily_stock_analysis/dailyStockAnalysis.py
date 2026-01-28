# mail parser plays the role of only sending the mail to an user 

# tasks executed by this module:
# 1.  recives the processed data in the form of a dict 
# 2.  uses the ollama model to conver that into user understandable form 
# 3.  Once that has been completed then the data is put into a html 
# 4.  Later the whole fucntion is called in the gmailSubscription.py file 

from datetime import datetime
import os
from datetime import date
import json , requests
from Stock_analysis_modules.collectedDataAnalysis import ollamaResponse , fetchCollectedData
# from dotenv import load_dotenv

DOCKER_PATH = os.environ.get("DOCKER_PATH")
DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


# used for testing 
# DATA_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/csvFiles"
# REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/reports"



def jsonFiltering(obj):
    if isinstance(obj, dict):
        return {k: jsonFiltering(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [jsonFiltering(v) for v in obj]
    elif hasattr(obj, "item"): 
        return obj.item()
    return obj





# def aiCheck(data):
#     start = time.perf_counter()
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": "phi3:mini",
#         "prompt": f"""
#                     {data}
                    
#                     Summarize the following stock-details JSON in under 100 words.
#                     Highlight major stocks and important trends only.
#                     No bullet points. No extra explanation.
#                     Stop immediately once the limit is reached.
    

#                     """,
#         "stream": False,
#         "tokens" : False
#     }

#     response = requests.post(url, json=payload)
#     response.raise_for_status()  # crashes loudly if Ollama is unhappy
#     end = time.perf_counter()
#     totaltime = end - start
#     # print("--------------->" , totaltime)
#     print("--------------->", round(totaltime, 3), "seconds")
#     return response.json()["response"]






def mailParser():
    analyzedData = fetchCollectedData()
    # print(analyzedData)

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

            Adddate = date.today().strftime("%d-%m-%Y")

            cleaned_stock = jsonFiltering(data)
            cleaned_stock["date"] = Adddate
            file_data.append(cleaned_stock)

            # print("------->", file_data)
            # aiResponse = aiCheck(file_data)
            # print("AI RESPONSE ---->" , aiResponse)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(file_data, file, indent=1)

            print("DATA WAS ADDED AS JSON FORM SUCCESSFULLY...")

        except OSError as error:
            print("FAILED TO ADD JSON WITH ERROR :" , error)

def main():
    print("RUNNING DAILY STOCK ANALYSIS ...")
    mailParser()



# print("------------------->",data)
# output = aiCheck()
# print(output)
# mailParser()

# the function mailParser is being called within the gmailSubscription 