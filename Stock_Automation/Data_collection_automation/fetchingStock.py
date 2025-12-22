#this file is mainly responsible for the fetching of the stocks that he user has added , the stock price along with date and time is fetched here 
#once the fetching is done then it adds that data into a csv in realtime making the data more analysable 
#the data is then analyzed by another file and send via mail

import requests
import time , csv
import os
from concurrent.futures import ThreadPoolExecutor
from Data_fetching_from_db.fetching_tokenization import fetchingUserAddedStock




HEADER = ["EXTRACTED_DATE","EXTRACTED_TIME","STOCK_NAME","EXTRACTED_PRICE"]

def priceFetcher(stockName):

    url = f"https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol={stockName}"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    CSV_DIR = os.path.join(
        BASE_DIR,
        "Data_collection_automation",
        "Analysed_Files_data",
        "csvFiles"
    )

    os.makedirs(CSV_DIR ,exist_ok=True)

    file_path = os.path.join(CSV_DIR , f"{stockName}.csv")
    


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
            time.sleep(30) 


        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("THREAD CRASHED WITH:", repr(e))
            raise




def main () :

    stocks = fetchingUserAddedStock()

    if not stocks: 
        print("No stock was extracted from db : FROM fetchingStocks.py")

    try : 
        with ThreadPoolExecutor(max_workers=len(stocks)) as executor:
            executor.map(priceFetcher, stocks)
    except KeyboardInterrupt : 
        print("FETCHING STOCK STOPPED BY KEYBOARD..")
