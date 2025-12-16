import requests
import time , csv
import os

stockName = "YESBANK"

url = f"https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol={stockName}"

HEADER = ["EXTRACTED_DATE","EXTRACTED_TIME","STOCK_NAME","EXTRACTED_PRICE"]


try : 
    while url :

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
        file_exists = os.path.isfile(f"./{stockName}.csv")


        # /app/input.csv ---> use this when running the code on the local docker also keeo cahanging the path
        # ./input.csv  ---> using this in the azure vm change if any error comes
        # /data/input.csv --. this has been used for the vm where we run the docker with this command [docker run -d   -v ~/stock-data:/data   testing]
        with open(f"./{stockName}.csv" , "a" , newline="") as f:
            writer = csv.writer(f)

            if not file_exists : 
                writer.writerow(HEADER) # adding the header if the file doesnt exist

            writer.writerow([date,currentTime,name,price]) #if file already exist this will start writing the row , will also come bellow the header
        time.sleep(20)  


except requests.exceptions.RequestException as e:
    print("Error:", e)