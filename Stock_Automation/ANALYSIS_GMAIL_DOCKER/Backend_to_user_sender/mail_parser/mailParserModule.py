from datetime import datetime
import os
import time
from Stock_analysis_modules.collectedDataAnalysis import ollamaResponse , fetchCollectedData
# from dotenv import load_dotenv

DOCKER_PATH = os.environ.get("DOCKER_PATH")
# DOCKER_PATH = "/home/saifmk10/AGENT-DATA/Stock-Data/TEST"
REPORT_DIR = os.path.join(DOCKER_PATH , "reports")

def mailParser():

    start = time.perf_counter()
    
    analyzedData = fetchCollectedData()

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

        # cleaningData()

    return report


    end = time.perf_counter()
    print("TIME TAKEN --->" , end - start)

final = mailParser()
print(final)

# the function mailParser is being called within the gmailSubscription 