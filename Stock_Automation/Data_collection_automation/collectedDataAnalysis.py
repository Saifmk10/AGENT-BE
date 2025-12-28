# this file plays the main role for the analysis where the data that is saved in the csv by the data fetching code is analysed
# once this data has been analysed the data is then added into the html format for the mail automation
# the mail automation does not happen from this file and happens in the gmailSubscription.py
# [NOTE] the data collected needs to be analysed again and then segeregated with the help of test conditions 


import csv
import pandas as pd
from pathlib import Path
from google import genai
from api_key import key
import os , time



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # fetching the root path
  # print(BASE_DIR)

DATA_DIR = os.path.join(
     BASE_DIR,
     "Data_collection_automation",
     "Analysed_files_data",
     "csvFiles", 
  )

stockUsers = os.listdir(DATA_DIR)

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



  # the report is parsed based on the information that has been collected and analyzed by the pandas
  

    # output_file = Path("./Analysed_Files_data/reports") / f"{stockName}_analysis_report.txt"

    # with open(output_file, "w" , encoding="utf-8") as file:
    #     file.write(report)

    return snapshot


 
# ======> add new features into this once this starts working [MAINLY THE VISUALIZATION] <========



# this function takes in the output from the analysispanda and then adds a summary that the users can understand easily
def geminiResponse (analysis):
    API_KEY = key
    client = genai.Client(api_key=API_KEY)


    try :   
      report = analysis
      response = client.models.generate_content(
      model="gemini-3-flash-preview",
      # contents=report + "You are given dict content related to a stock. Task: Convert this into useful insights a user can use to decide about the stock.Rules:- Limit the response to 200 words- Output only plain text- Do not use any symbols except the rupee symbol ₹- Start with one short hero paragraph- After that, write multiple short points, each on a new line- Do not use bullet symbols like -, *, or •"

      contents = f"""
                      {report}

                      You are given analyzed stock data.

                      Task:
                      Generate useful insights that help a user decide about the stock.

                      Strict output rules:
                      - Output ONLY valid HTML markup
                      - DO NOT include <html>, <head>, <body>, or <!DOCTYPE>
                      - The output must be suitable to paste directly inside an existing <div>
                      - Use only basic HTML tags such as <p>, <div>, <br>, <strong>, <span>
                      - Do NOT include markdown or explanations
                      - Do NOT include bullet symbols like -, *, or •
                      - Do NOT include any symbols except the rupee symbol ₹
                      - Limit the content to 200 words

                      Structure:
                      - Start with one short hero paragraph wrapped in a <p> tag
                      - Follow with multiple short insight paragraphs separated using <br /><br />

                      Generate only the HTML fragment now.
                  """



      )

      # print(response.text)
      return response.text
    except Exception as error : 
       print(error , "error in collectedDataAnalysis")



# function plays a role of validation and authentication , where a map and key is created for each user and the stock that the user has added , this map and key can be used for the stocks authentication
def usersAndStocksMap():
  usersAndStocks = {}

  # loop that loops through all the users who has added stock and the data has been colected already , the data is then accessed throught this loop for analysis
  for users in stockUsers:
    try:
      filesAdded = os.path.join(BASE_DIR,"Data_collection_automation","Analysed_files_data","csvFiles", users)

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

  for singleUser in stockUsers:
    try :
      path =  os.path.join(BASE_DIR,"Data_collection_automation","Analysed_files_data","csvFiles", singleUser)
      stocksAdded = os.listdir(path)
      print(stocksAdded)
      
      for stocks in stocksAdded:
        collectedPath =  os.path.join(BASE_DIR,"Data_collection_automation","Analysed_files_data","csvFiles", singleUser , stocks)
        print(stocks , " PATH : " , collectedPath)

        snapshot = analysisPandas(collectedPath)
        aiResponse = geminiResponse(snapshot)

        # print(stocks , " ANALYSED DATA :", snapshot)
        # print(stocks , " AI RESPONSE :", aiResponse)


        report = f"""
                <!DOCTYPE html>
                  <html lang="en">
                  <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>Stock Report</title>
                  </head>

                  <body style="margin:0;padding:0;background-color:#f0f1f5;font-family:Arial,Helvetica,sans-serif;color:#222222;">

                    <div style="max-width:600px;margin:0 auto;background-color:#ffffff;">

                      <!-- Header -->
                      <div style="display:flex;align-items:center;padding:20px;gap:12px;">
                        <img src="./logo.png" alt="Logo" style="width:28px;height:28px;display:block;" />
                        <div style="font-size:28px;font-weight:700;">FinTech</div>
                      </div>

                      <!-- Hero -->
                      <div>
                        <img src="https://raw.githubusercontent.com/Saifmk10/AGENT-BE/main/Stock_Automation/Data_collection_automation/hero.png" alt="Stock Report" style="width:100%;height:auto;display:block;"  />

                      </div>

                      <!-- Summary -->
                      <div style="padding:20px;font-size:16px;line-height:1.4;text-align:center;">
                        We collected a total of <strong>{snapshot["count"]}</strong> price points.<br />
                        Here’s your stock report.
                      </div>

                      <div style="height:1px;background-color:#bfc3c8;margin:20px 0;"></div>

                      <!-- Central Tendency -->
                      <div style="padding:20px;font-size:16px;line-height:1.4;">
                        <h3 style="margin-top:0;text-decoration:underline;">Central Tendency</h3>
                        Mean Price: <strong>₹{ snapshot["mean"]:.2f}</strong><br /><br />
                        Median Price: <strong>₹{snapshot["median"]:.2f}</strong><br /><br />
                        <span style="background-color:#fcfd5a;padding:2px 4px;font-weight:600;">
                          Prices remained tightly clustered around the median.
                        </span>
                      </div>

                      <div style="height:1px;background-color:#bfc3c8;margin:20px 0;"></div>

                      <!-- Distribution -->
                      <div style="padding:20px;font-size:16px;line-height:1.4;">
                        <h3 style="margin-top:0;text-decoration:underline;">Price Distribution</h3>
                        Minimum: <strong>₹{snapshot["min"]:.2f}</strong><br /><br />
                        Maximum: <strong>₹{snapshot["max"]:.2f}</strong><br /><br />
                        IQR (25%–75%): <strong>₹{snapshot["q25"]:.2f} – ₹{snapshot["q75"]:.2f}</strong><br /><br />
                        <span style="background-color:#fcfd5a;padding:2px 4px;font-weight:600;">
                          Majority of trades occurred in a narrow band.
                        </span>
                      </div>

                      <div style="height:1px;background-color:#bfc3c8;margin:20px 0;"></div>

                      <!-- Volatility -->
                      <div style="padding:20px;font-size:16px;line-height:1.4;">
                        <h3 style="margin-top:0;text-decoration:underline;">Volatility</h3>
                        Standard Deviation: <strong>₹{snapshot["std"]:.3f}</strong><br /><br />
                        Intraday Range: <strong>₹{snapshot["range"]:.2f}</strong><br /><br />
                        Percentage Movement: <strong>{snapshot["percentage"]:.2f}%</strong><br /><br />
                        <span style="background-color:#fcfd5a;padding:2px 4px;font-weight:600;">
                          Overall volatility remained low.
                        </span>
                      </div>

                      <div style="height:1px;background-color:#bfc3c8;margin:20px 0;"></div>

                      <!-- Interpretation -->
                      <div style="padding:20px;font-size:16px;line-height:1.4;text-align:center;">
                        <h3 style="margin-top:0;text-decoration:underline;">Market Interpretation</h3>
                        {aiResponse}
                      </div>

                      <!-- Footer -->
                      <div style="background-color:#070300;color:#f6f5f1;padding:25px 20px;font-size:14px;">
                        <strong>Contact Developer</strong><br /><br />
                        Call: <a href="tel:+918867715967" style="color:#f6f5f1;text-decoration:none;">+91 8867715967</a><br />
                        Email: <a href="mailto:saifmkpvt@gmail.com" style="color:#f6f5f1;text-decoration:none;">saifmkpvt@gmail.com</a><br /><br />

                        <div style="color:#bfc3c8;font-size:13px;">
                          Bengaluru, Karnataka, India
                        </div>

                        <div style="color:#666666;font-size:12px;font-style:italic;margin-top:16px;">
                          This report is auto-generated for informational purposes only.
                          Do not rely on it as the sole basis for investment decisions.
                        </div>
                      </div>

                    </div>

                  </body>
                  </html>
            """


        print("FINAL REPORT : " , report)
    except Exception as error:
       print("Error from collectedDataAnalysis.py" , error)

  end = time.perf_counter()

  print("TIME TAKEN --->" , end - start)


  # the report is parsed based on the information that has been collected and analyzed by the pandas
  
  # print(report)
  # # print(aiResponse)
  # return report
mailParser()
