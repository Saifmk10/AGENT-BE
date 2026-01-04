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



BASE_DIR = os.environ.get("BASE_DIR", os.getcwd()) # fetching the root path
# print(BASE_DIR)

DATA_DIR = os.path.join(
     BASE_DIR,
     "Data_collection_automation",
     "Analysed_Files_data",
     "csvFiles", 
  )

REPORT_DIR = os.path.join(
    BASE_DIR,
     "Data_collection_automation",
     "Analysed_Files_data",
     "reports", 
)

# function that makes sure the folders are created , as the folders are ignored my default 
def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


# stockUsers = os.listdir(DATA_DIR)

# bellow code is only for the purpose of testing and not for preoduction

# def readingData() : 
    
#     with open ("./YESBANK.csv" , mode="r" , newline="") as file :
#         reader = csv.DictReader(file)
#         container = []

#         for rows in reader : 

#             container.append({
#                 "date": rows["EXTRACTED_DATE"],
#                 "time": rows["EXTRACTED_TIME"],
#                 "price": rows["EXTRACTED_PRICE"],
#             })
            
#         return container 
        

# function reposnsible for the main analysis of that data that has been collected
def analysisPandas (path): 
    
    stockName = path.rsplit("." , 1)[0]

    dataFrame = pd.read_csv(path)
    snapshot = {
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
        "range" : dataFrame["EXTRACTED_PRICE"].max() - dataFrame["EXTRACTED_PRICE"].min() 
    }
    # print(snapshot["percentage"])

    return snapshot


# ======> add new features into this once this starts working [MAINLY THE VISUALIZATION] <========


# this function takes in the output from the analysispanda and then adds a summary that the users can understand easily
def geminiResponse (analysis):
    API_KEY = key
    client = genai.Client(api_key=API_KEY)

    try :   
        report = analysis
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            {report}
            """
        )

        # print(response.text)
        return response.text
    except Exception as error : 
        print(error , "error in collectedDataAnalysis")



# this function plays the role of the ai parsed message , there is a pre entered prompt that is used within the model where the data from the stock is added into this function to get a parsed user underatable output
ollama_warmed = False  # module-level flag
def ollamaResponse(data):
    global ollama_warmed
    url = "http://localhost:11434/api/generate"

    # 🔹 One-time warm-up
    if not ollama_warmed:
        try:
            requests.post(
                url,
                json={
                    "model": "phi3:mini",
                    "prompt": "OK",
                    "options": {
                        "num_predict": 1,
                        "temperature": 0
                    },
                    "stream": False
                },
                timeout=10
            )
        except Exception:
            pass
        ollama_warmed = True

    # 🔹 Structured plain-text prompt
    prompt = f"""
                You are analysing stock performance data for a cautious investor.

                DATA:
                {data}

                YOUR GOAL:
                Turn the data into clear, practical insights that help a cautious investor understand the stock.

                OUTPUT RULES (VERY IMPORTANT):
                - Write EXACTLY 4 lines
                - Do NOT use HTML
                - Do NOT use bullet points or symbols
                - Each line MUST start with one of these labels (no other labels allowed):
                  SUMMARY:
                  POSITIVE:
                  NEGATIVE:
                  DECISION:

                CONTENT GUIDELINES:
                - SUMMARY:
                  Describe the recent price behaviour and overall trend.
                  Length: 20–35 words.

                - POSITIVE:
                  Mention the strongest positive or supportive signal, if any.
                  Length: 15–30 words.

                - NEGATIVE:
                  Mention the main risk, weakness, or concern.
                  Length: 15–30 words.

                - DECISION:
                  Write ONLY ONE word — either BUY or AVOID.

                DECISION LOGIC:
                - If price movement is weak, unclear, sideways, or range-bound → AVOID
                - Only write BUY if the movement is clearly directional and stable

                CURRENCY RULES:
                - You may use ONLY the rupee symbol ₹ and the dollar symbol $
                - Do NOT use any other currency symbols

                FINAL INSTRUCTION:
                Return ONLY the 4 labelled lines.
                Do not add explanations, greetings, or extra text.
                """


    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "options": {
            "num_predict": 100,
            "temperature": 0.2
        },
        "stream": False
    }

    try:
        res = requests.post(url, json=payload, timeout=120)
        text = res.json().get("response", "")

        # 🔹 Parse response
        summary = positive = negative = decision = ""

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("POSITIVE:"):
                positive = line.replace("POSITIVE:", "").strip()
            elif line.startswith("NEGATIVE:"):
                negative = line.replace("NEGATIVE:", "").strip()
            elif line.startswith("DECISION:"):
                decision = line.replace("DECISION:", "").strip().upper()

        # 🔹 Build HTML deterministically
        html = []

        if summary:
            html.append(f"<p>{summary}</p>")

        if positive:
            html.append(f"<p>{positive}</p>")

        if negative:
            html.append(f"<p>{negative}</p>")

        if decision == "BUY":
            html.append(
                "<p style='background-color:#e6f7e6;'><strong>BUY</strong></p>"
            )
        else:
            html.append(
                "<p style='background-color:#fdecea;'><strong>AVOID</strong></p>"
            )

        return "".join(html)

    except requests.exceptions.ReadTimeout:
        return "<p>AI analysis timed out due to system load.</p>"

    except Exception:
        return "<p>AI analysis unavailable.</p>"

# function plays a role of validation and authentication , where a map and key is created for each user and the stock that the user has added , this map and key can be used for the stocks authentication
def usersAndStocksMap():
    usersAndStocks = {}
    stockUsers = os.listdir(DATA_DIR)
    # loop that loops through all the users who has added stock and the data has been colected already , the data is then accessed throught this loop for analysis
    for users in stockUsers:
        try:
            filesAdded = os.path.join(BASE_DIR,"Data_collection_automation","Analysed_Files_data","csvFiles", users)

            fileContent = os.listdir(filesAdded)     

            if users not in usersAndStocks:
                usersAndStocks[users] = []

            # content = {users : fileContent}
            usersAndStocks[users].append(fileContent) # this is the key added to the map here

        except Exception as error : 
            print("error in collectedDataAnalysis.py : " , error)

    return usersAndStocks



# this is the main function where all the analysis and the ai parsing will come together and then will be put together into the html format that will be send via mail
# the path for the analysisPanda function is being added within this function
# [NOTE] : need to add the iteration where all the stocks csv will be added analyzed one after the other
def mailParser():

    start = time.perf_counter()
    usersAndStocks = {}
    analyzedData = {}
    stockUsers = os.listdir(DATA_DIR)

    for singleUser in stockUsers:

        analyzedData.setdefault(singleUser, [])

        try :
            #fetching the path where the data has been stored asper the user , for loop loops through all the email ids present 
            path =  os.path.join(BASE_DIR,"Data_collection_automation","Analysed_Files_data","csvFiles", singleUser)
            stocksAdded = os.listdir(path)
            print("LOOKING AT USER --->" , singleUser)

            # this for loop then moves into the user email folder and fetch the path to all the stocks that has been added so it can use the panda function for analysis
            for stocks in stocksAdded:
                collectedPath =  os.path.join(BASE_DIR,"Data_collection_automation","Analysed_Files_data","csvFiles", singleUser , stocks)

                #calling the analysis funtions to fetch the data from the analysis 
                snapshot = analysisPandas(collectedPath) # analyzed data that contains the data that has all mean median etc

                try : 
                    # this is a dict , where all the users email , stocks they added , that stocks analysis is put into one place
                    # this is done so that each user will get 1 api call for all the stocks reducing cost.
                    # adding the snapshot alone into the ai is enought but then ive added the stock name too , just incase
                    analyzedData[singleUser].append({
                        "stocks" : stocks,
                        "analysis" : snapshot, 
                    })

                except Exception as error:
                    print("error in dict in collectedDataAnalysis.py:" , error)

        except Exception as error:
            print("Error from collectedDataAnalysis.py" , error)


    # loops plays an imp role where it makes sure that each users get just 1 api call , all the data has been added into the analyzedData as seen above and this data is used here to get the ai summary
    # the ai summary is then added into the report [NOTE]: for now 
    # then the complete report is then saved into a folder called reports from where the mail will be sent
    # this loop is resent in the outer loop so each user gets only 1 iteration and making sure there is no data disputes happening in between
    for userEmail , usersData in analyzedData.items():

        report = f"""
                  <!DOCTYPE html>
                  <html lang="en">
                  <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>Stock Report</title>
                  </head>

                  <body style="margin:0;padding:0;background-color:#f0f1f5;
                               font-family:Arial,Helvetica,sans-serif;color:#222222;">

                    <div style="max-width:600px;margin:0 auto;background-color:#ffffff;">

                      <!-- Header -->
                      <div style="display:flex;align-items:center;padding:20px;gap:12px;">
                        <img src="./logo.png" alt="Logo" style="width:28px;height:28px;" />
                        <div style="font-size:28px;font-weight:700;">FinTech</div>
                      </div>

                      <!-- Hero -->
                      <div>
                        <img src="https://raw.githubusercontent.com/Saifmk10/AGENT-BE/main/Stock_Automation/Data_collection_automation/hero.png"
                             style="width:100%;height:auto;display:block;" />
                      </div>
                  """

        for stockData in usersData:
            a = stockData["analysis"] # this contains all the details about the stock mean median all those
            stock = stockData["stocks"].replace(".csv", "") #fetching individual stock name
            aiResponse = ollamaResponse({"analysis" : a , "stockName" :stock})
            print(stock , "--->" , aiResponse)

            report += f"""
                          <div style="padding:20px;">
                            <h3 style="margin-top:0;text-align:center;text-decoration:underline;">
                              {stock}
                            </h3>

                            <table width="100%" cellpadding="8" cellspacing="0"
                                   style="border-collapse:collapse;font-size:15px;">

                              <tr style="background-color:#f3f4f6;">
                                <th style="border:1px solid #ccc;">Metric</th>
                                <th style="border:1px solid #ccc;">Value</th>
                              </tr>

                              <tr><td style="border:1px solid #ccc;">Data Points</td><td style="border:1px solid #ccc;">{int(a["count"])}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Mean Price</td><td style="border:1px solid #ccc;">₹{float(a["mean"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Median Price</td><td style="border:1px solid #ccc;">₹{float(a["median"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Lowest Price</td><td style="border:1px solid #ccc;">₹{float(a["min"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Highest Price</td><td style="border:1px solid #ccc;">₹{float(a["max"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">25% Quartile</td><td style="border:1px solid #ccc;">₹{float(a["q25"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">75% Quartile</td><td style="border:1px solid #ccc;">₹{float(a["q75"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Price Range</td><td style="border:1px solid #ccc;">₹{float(a["range"]):.2f}</td></tr>
                              <tr><td style="border:1px solid #ccc;">Percentage Movement</td><td style="border:1px solid #ccc;">{float(a["percentage"]):.2f}%</td></tr>
                              <tr><td style="border:1px solid #ccc;">Standard Deviation</td><td style="border:1px solid #ccc;">₹{float(a["std"]):.3f}</td></tr>

                            </table>
                          </div>

                          <div style="padding:20px;font-size:16px;line-height:1.4;text-align:center;">
                            <h3 style="margin-top:0;text-decoration:underline;">Market Interpretation</h3>
                            {aiResponse}
                          </div>

                          <div style="height:1px;background-color:#bfc3c8;margin:20px 0;"></div>
                      """                     

            time.sleep(10)

        report += f"""
                          <!-- Footer -->
                          <div style="background-color:#070300;color:#f6f5f1;padding:25px 20px;font-size:14px;">
                            <strong>Contact Developer</strong><br /><br />
                            Call: <a href="tel:+918867715967" style="color:#f6f5f1;">+91 8867715967</a><br />
                            Email: <a href="mailto:saifmkpvt@gmail.com" style="color:#f6f5f1;">saifmkpvt@gmail.com</a>
                          </div>

                        <div style="color:#666666;font-size:12px;font-style:italic;margin-top:16px;">
                          This report is auto-generated for informational purposes only.
                          Do not rely on it as the sole basis for investment decisions.
                        </div>
                      </body>
                    </html>
                  """

        
        
           
        #this is used to add the date , so that can be used as the file name easy to access and analyze
        today = datetime.now()
        dateFormat = today.strftime("%-d-%b-%Y").lower()  
        file_name = f"{dateFormat}.html"


        # checking if the file is available within the folder , if not available then the file and the folder both will be created
        user_dir = os.path.join(REPORT_DIR, userEmail)
        os.makedirs(user_dir, exist_ok=True)

        # joining the path together to write the data into that location
        file_path = os.path.join(user_dir, file_name)

        # writing the report data into the file created
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(report)




    end = time.perf_counter()
    print("TIME TAKEN --->" , end - start)



# the function mailParser is being called within the gmailSubscription 
