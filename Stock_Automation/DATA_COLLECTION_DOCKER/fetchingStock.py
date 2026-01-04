#this file is mainly responsible for the fetching of the stocks that he user has added , the stock price along with date and time is fetched here 
#once the fetching is done then it adds that data into a csv in realtime making the data more analysable 
#the data is then analyzed by another file and send via mail

import requests
import time , csv
import os
from concurrent.futures import ThreadPoolExecutor
from Data_fetching_from_db.fetching_tokenization import fetchingUserAddedStock



HEADER = ["EXTRACTED_DATE","EXTRACTED_TIME","STOCK_NAME","EXTRACTED_PRICE"]
fetchingDBData = fetchingUserAddedStock() # using the data that was fetched form the db
stock_to_emails = {}
print("Stocks added and users list" , fetchingDBData)

# the data that was fetched is not converted into a key value pair so only the user subscribed stocks will be added to his repo
for user in fetchingDBData:
    email = user["email"]
    for stock in user["stocks"]:
        stock_to_emails.setdefault(stock, []).append(email)



# this function plays the main role where the data (stock price) is collected on a loop and saved in a csv file for the other modules to analyze later
def priceFetcher(stockName):

    url = f"https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol={stockName}"
    
    
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
            response = requests.get(url)
            print("response : " , response.status_code)
            print(response.json())
            data = response.json()


            #here the current data and time will be added into the csv
            date = time.strftime("%d-%m-%Y", time.localtime())
            currentTime = time.strftime("%H:%M:%S", time.localtime())


            # these collect the exact data that has been generated from the json repsonse and then added into the csv
            price = float(data["stockPrice"])
            name = data["stockName"]


            # using the key value pair mentioned above to add the data into the respective path
            for email in stock_to_emails.get(stockName, []):
                print(email)
                CSV_DIR = os.path.join(
                    BASE_DIR,
                    "Data_collection_automation",
                    "Analysed_Files_data",
                    "csvFiles",
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
                    writer.writerow([date,currentTime,name,price]) #if file already exist this will start writing the row , will also come bellow the header

            time.sleep(30)  #[NOTE]change to 300 in prod =================<>=======================

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("THREAD CRASHED WITH [ln 90]:", repr(e))
            raise


# main function is the runnnig function this is executed with the help of the run.py function, done to prevent the modules and folder conflicts
def main () :

    jobs = set()

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
