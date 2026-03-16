# Weekly analysis helps in analysis of the stock on a weekly basis , the json that is generated intraday for each user is used for getting the weekly stock analysis

# tasks executed by this module:
# 1.  converts the josn into a df and then perform analysis using the df 
# 2.  adds llm geneated summary into the stock making sure users understand it in plain english
# 3.  new updated json is then added into the dir


from datetime import datetime
from zoneinfo import ZoneInfo
import time
from threading import Lock
import os
# from datetime import date
import json 
import pandas as pd
import google.genai as genai
from google.genai import types
# from Stock_analysis_modules.collectedDataAnalysis import  fetchCollectedData
# from Csv_path_cleaner.cleaningCollectedCsv import cleaningData # =====> change this later
# from Daily_stock_analysis.DbOperations.intraDayDataToDB import updatingIntrDay
from LLM_API_KEYS import gemini_api_key
# from dotenv import load_dotenv

# [NOTE] docker path used for prod only
# DOCKER_PATH = os.environ.get("DOCKER_PATH")
# DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
# REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


# [NOTE] used for testing 
FINAL_REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/weekly_report/"
REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/weekly_report/data"

LAST_GEMINI_CALL = 0
GEMINI_LOCK = Lock()
GEMINI_COOLDOWN = 2.5 

users = os.listdir(REPORT_DIR)
print(users)



# gemini ai summary , provides the summary for the current day data
def aiSummary(data):
    global LAST_GEMINI_CALL

    LLM_MODEL = ["gemini-3-flash-preview",
        "gemini-2.5-flash",
        "gemini-2.0-flash"]

    with GEMINI_LOCK:
        now = time.time()
        remaining = GEMINI_COOLDOWN - (now - LAST_GEMINI_CALL)
        if remaining > 0:
            time.sleep(remaining)
        LAST_GEMINI_CALL = time.time()

    start = time.perf_counter()

    client = genai.Client(api_key=gemini_api_key)

    prompt = f"Analyze: {data}"

    for models in LLM_MODEL:
        try : 

            print("Trying model:", models)

            response = client.models.generate_content(
                model=models,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        """
                        Act as a Senior Market Strategist. Analyze the weekly JSON data for one or more stocks.
                        Output MUST be a single Python-parsable dictionary where keys are stock tickers and values are the analysis strings.

                        Logic:
                        1. Trend: net_weekly_return > 3% (Strong Growth), < -3% (Correction).
                        2. Energy: volatility_expansion_ratio > 3.0 (Trend Breakout), < 1.5 (Stagnant).
                        3. Flow: volume_conviction_score > 1.5 (Institutional Accumulation), < 0.8 (Low Interest).
                        4. Floor: liquidity_absorption_rate > 0.5 (Strong Support).
                        5. Signal: consolidation_squeeze_alert == "Yes" (Coiled Spring).

                        Structure for each analysis value:
                        - Headline: Bold, 1-sentence summary.
                        - Key Takeaway: 1-sentence primary signal.
                        - Narrative: Professional explanation of buyer/seller positioning (100-130 words).

                        Rules: 
                        - Return ONLY the dictionary. 
                        - NO raw numbers or JSON keys in the narrative text. 
                        - NO financial advice. 
                        - Use \n for newlines within the dictionary values.

                        """
                    ),
                    temperature=0.1,
                )
            )


            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Empty response from Gemini")

            print(f"Gemini time: {round(time.perf_counter() - start, 3)}s")
            print(f"Input Tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Output Tokens: {response.usage_metadata.candidates_token_count}")
            print(f"Total Tokens: {response.usage_metadata.total_token_count}")
            return text.strip()

        except Exception as error:
            print("ERROR IN GEMINI RESPONSE :" , error)






def dataframeConvertion():

    try:
        for user in users:

            userPath = os.path.join(REPORT_DIR, user)
            print(userPath)

            rows = []

            for file in os.listdir(userPath):

                dailyreportPath = os.path.join(userPath, file)
                print(dailyreportPath)

                with open(dailyreportPath, "r") as f:
                    fileContent = json.load(f)

                for items in fileContent["HISTORY"]:
                    date = items["date"]
                    summary = items["summary"]

                    for stockDetails in items["report"]:
                        stock = stockDetails["stocks"]
                        analysis = stockDetails["analysis"]

                        row = {
                            "date": date,
                            "summary": summary,
                            "stock": stock
                        }

                        row.update(analysis["stats"])
                        row.update(analysis["ohlc"])
                        row.update(analysis["signal"])
                        row.update(analysis["advanced"])

                        rows.append(row)

            dataFrame = pd.DataFrame(rows)

            print("NEW DATA FRAME:", dataFrame)

            report = []

            for stock, df in dataFrame.groupby("stock"):

                totalWeeklyReturn = ((df['stock_current'].iloc[-1] - df['previous_close'].iloc[0]) / df['previous_close'].iloc[0]) * 100
                volatalityExpansionRation = df['range'].max() / df['range'].min()
                institutionalFlow = df['rvol'].iloc[-1]
                behaviouralBias = df['Late_Buying'].mean()
                absorptionRate = df['Dip_Absorption'].mean()
                squeezeDetcted = "Yes" if df['range'].min() < (df['range'].mean() * 0.6) else "No"

                finalReport = {
                    "net_weekly_return": float(totalWeeklyReturn),
                    "volatility_expansion_ratio": float(volatalityExpansionRation),
                    "volume_conviction_score": float(institutionalFlow),
                    "closing_sentiment_bias": float(behaviouralBias),
                    "liquidity_absorption_rate": float(absorptionRate),
                    "consolidation_squeeze_alert": squeezeDetcted
                }

                report.append({
                    "stock": stock,
                    "report": finalReport
                })

            currentDate = datetime.now().strftime("%d-%m-%Y")
            ist = datetime.now(ZoneInfo("Asia/Kolkata"))
            currentTime = ist.strftime("%H:%M:%S")

            # ---- SINGLE AI CALL ----
            forAi = {
                "stocks": report
            }

            aiReport = aiSummary(forAi)

            finalOutput = {
                "date": currentDate,
                "time": currentTime,
                "stocks": report,
                "summary": aiReport
            }

            print("FINAL REPORT FOR USER ----->", user, ":", finalOutput)

            WRITE_PATH = os.path.join(FINAL_REPORT_DIR, "report" ,f"{user}.json")

            try:
                os.makedirs(os.path.dirname(WRITE_PATH), exist_ok=True)
                with open(WRITE_PATH , "w") as file:
                    json.dump(finalOutput , file , indent=4)
            except OSError as error:
                print("FAILED TO ADD USER DATA INTO PATH [error]:" , error)
    except Exception as error:
        print("ERROR CASUED IN WEEEKLY DATA ANALYSIS [error]:" , error)




dataframeConvertion()


