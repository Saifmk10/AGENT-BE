import csv
import pandas as pd


def readingData() : 
    
    with open ("./YESBANK.csv" , mode="r" , newline="") as file :
        reader = csv.DictReader(file)
        container = []

        for rows in reader : 

            container.append({
                "date": rows["EXTRACTED_DATE"],
                "time": rows["EXTRACTED_TIME"],
                "price": rows["EXTRACTED_PRICE"],
            })
            
        return container 
        

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
    report = f"""
                <html>
                  <body style="
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 14px;
                    color: #1a1a1a;
                    line-height: 1.5;
                  ">

                    <p>Dear User,</p>

                    <p>
                      Please find below the daily stock price analysis summary based on available intraday market data.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <h3 style="margin-bottom: 6px;">Data Summary</h3>
                    <p style="margin-top: 0;">
                      A total of <b>{snapshot["count"]}</b> price observations were analyzed during the trading session.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <h3 style="margin-bottom: 6px;">Central Tendency</h3>
                    <p style="margin: 4px 0;">
                      Mean Price: <b>₹{snapshot["mean"]:.2f}</b><br>
                      Median Price: <b>₹{snapshot["median"]:.2f}</b>
                    </p>
                    <p style="margin-top: 6px;">
                      Prices remained tightly clustered around the median, indicating limited dispersion.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <h3 style="margin-bottom: 6px;">Price Distribution</h3>
                    <p style="margin: 4px 0;">
                      Minimum: <b>₹{snapshot["min"]:.2f}</b><br>
                      Maximum: <b>₹{snapshot["max"]:.2f}</b><br>
                      Interquartile Range (25%–75%): <b>₹{snapshot["q25"]:.2f} – ₹{snapshot["q75"]:.2f}</b>
                    </p>
                    <p style="margin-top: 6px;">
                      The majority of trades occurred within a narrow price band, reflecting strong price consolidation.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <h3 style="margin-bottom: 6px;">Volatility</h3>
                    <p style="margin: 4px 0;">
                      Standard Deviation: <b>₹{snapshot["std"]:.3f}</b><br>
                      Intraday Range: <b>₹{snapshot["range"]:.2f}</b><br>
                      Percentage Movement: <b>{snapshot["percentage"]:.2f}%</b>
                    </p>
                    <p style="margin-top: 5px;">
                      Overall volatility remained low throughout the session.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <h3 style="margin-bottom: 6px;">Market Interpretation</h3>
                    <p style="margin-top: 0;">
                      The stock exhibited range-bound behavior with no meaningful directional trend.
                      Price action remained stable, indicating limited intraday momentum.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 5px 0;">

                    <p style="font-size: 12px; color: #666;">
                      <i>
                        Disclaimer: This report is automatically generated for informational purposes only.
                        While reasonable care has been taken to ensure accuracy, it should not be relied upon
                        as the sole basis for investment decisions. Please refer to the official stock exchange
                        or company website for authoritative and up-to-date information.
                      </i>
                    </p>

                    <p style="margin-top: 10px;">
                      Regards,<br>
                      <b>Automated Market Analysis System</b>
                    </p>

                  </body>
                </html>
            """






    with open(f"./{stockName}_analysis_report.txt", "w" , encoding="utf-8") as file:
        file.write(report)

    return report





# print(analysisPandas("./YESBANK.csv"))