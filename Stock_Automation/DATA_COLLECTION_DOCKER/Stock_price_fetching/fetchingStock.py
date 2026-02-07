#this file is mainly responsible for the fetching of the stocks that he user has added , the stock price along with date and time is fetched here 
#once the fetching is done then it adds that data into a csv in realtime making the data more analysable 
#the data is then analyzed by another file and send via mail

import requests
import time , csv
import os
from concurrent.futures import ThreadPoolExecutor
from Data_fetching_from_db.fetching_tokenization import fetchingUserAddedStock

# DATA_DIR = "/home/saifmk10/AGENT-DATA/Stock-Data/TEST/csvFiles"
DOCKER_PATH = os.environ.get("DOCKER_PATH")
DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")

HEADER = ["EXTRACTED_DATE","EXTRACTED_TIME","STOCK_NAME","EXTRACTED_PRICE","STOCK_VOLUME","STOCK_AVG_VOLUME"] #header for the csv file

fetchingDBData = fetchingUserAddedStock() # using the data that was fetched form the db , the stocks that has been added by users will be fetched here
stock_to_emails = {}
print("Stocks added and users list" , fetchingDBData)

# the data that was fetched is not converted into a key value pair so only the user subscribed stocks will be added to his repo
for user in fetchingDBData:
    email = user["email"]
    for stock in user["stocks"]:
        stock_to_emails.setdefault(stock, []).append(email)



# this function plays the main role where the data (stock price) is collected on a loop and saved in a csv file for the other modules to analyze later
def priceFetcher(stockName):

    # url = f"https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol={stockName}"
    url = f"https://stock-api.saifmk.website/stock/{stockName}"
    
    
    # setting the path for adding the csv into (remains the same for the vm)
    # for each user a new folder will be created in his/her email id so segregation is simple and can avoid any kind of mix ups while sending the mail
    
    # emailDir = fetchingEmail['email']
    # print(emailDir)

    # FOR LOCAL TESTING
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    BASE_DIR = os.environ.get("BASE_DIR", os.getcwd())

    while True :
        try :
            # api calling 
            response = requests.get(url , timeout=10)
            print("response : " , response.status_code)
            
            response.raise_for_status()
            data = response.json()
            print(data)
            

            #here the current data and time will be added into the csv
            date = time.strftime("%d-%m-%Y", time.localtime())
            currentTime = time.strftime("%H:%M:%S", time.localtime())


            # these collect the exact data that has been generated from the json repsonse and then added into the csv
            name = data["stockName"]
            price = float(data["stockPrice"])
            volume = float(data["stockVolume"])
            avg_vol = float(data["stockAvgVolume"])
            



            # using the key value pair mentioned above to add the data into the respective path
            for email in stock_to_emails.get(stockName, []):
                print(email)
                CSV_DIR = os.path.join(
                    DATA_DIR,
                    email
                )
                os.makedirs(CSV_DIR ,exist_ok=True)
                file_path = os.path.join(CSV_DIR , f"{stockName}.csv")



                # checking if the file exist in the location , if it exist then the header wont be added and only data will be added
                # if file is not present the csv will be created and the header will also be added
                # file_exists = os.path.isfile(f"./Analysed_Files_data/csvFiles/{stockName}.csv")
                file_exists = os.path.isfile(file_path)


                # /app/input.csv ---> use this when running the code on the local docker also keeo cahanging the path
                # ./input.csv  ---> using this in the azure vm change if any error comes
                # f"/data/{stockName}.csv --> this has been used for the vm where we run the docker with this command [docker run -d   -v ~/stock-data:/data   testing]
                with open(file_path , "a" , newline="") as f:
                    writer = csv.writer(f)
                    if not file_exists : 
                        writer.writerow(HEADER) # adding the header if the file doesnt exist
                    writer.writerow([date,currentTime,name,price,volume,avg_vol]) #if file already exist this will start writing the row , will also come bellow the header

            time.sleep(300)  #[NOTE]change to 300 in prod =================<>=======================

        except KeyboardInterrupt:
            # raise
            print("KEYBOARD INTERRUPTION...") # only happens in the test , not in the container 

        except requests.exceptions.HTTPError as error :
            if error.response.status_code in (404 , 403 , 429 ): # will re run the try block 
                time.sleep(2)
                continue
            else:
                print("FETCHING FAILED DUE TO HTTP CODE :" , error)
                break
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            print("NETWORK ERROR, RETRYING:", error)
            time.sleep(2)
            continue
        except Exception as error:
            print("THREAD CRASHED WITH [ln 98]:", repr(error))
            # raise


# main function is the runnnig function this is executed with the help of the run.py function, done to prevent the modules and folder conflicts
def main () :

    jobs = set() # here the jobs are the stock name that is being fetched from the users who has the subscription

    for user in fetchingDBData:
        stockNames = user["stocks"]

        if not stockNames:
            continue

        for stock in stockNames:
            jobs.add(stock)

    try:
        with ThreadPoolExecutor(max_workers=min(5, len(jobs))) as executor:
            executor.map(priceFetcher, jobs)
    except KeyboardInterrupt:
        print("FETCHING STOCK STOPPED BY KEYBOARD..")

# main()