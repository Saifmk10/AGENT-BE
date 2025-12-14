import requests
import time , csv
import os

stockName = "YESBANK"

url = "https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol=YESBANK"


HEADER = ["EXTRACTED_DATE","EXTRACTED_TIME","STOCK_NAME","EXTRACTED_PRICE"]


try : 
    while url :
        response = requests.get(url)
        print("response : " , response.status_code)
        print(response.json())

        date = time.strftime("%d-%m-%Y", time.localtime())
        currentTime = time.strftime("%H:%M:%S", time.localtime())
        data = response.json()
        # print(price["stockPrice"])

        price = float(data["stockPrice"])
        name = data["stockName"]
        # file_empty = os.makedirs("/data/input.csv", exist_ok=True) and os.stat("/data/input.csv").st_size == 0
        file_exists = os.path.isfile("/data/input.csv")


        # /app/input.csv ---> use this when running the code on the local docker also keeo cahanging the path
        # ./input.csv  ---> using this in the azure vm change if any error comes
        # /data/input.csv
        with open("/data/input.csv" , "a" , newline="") as f:
            writer = csv.writer(f)

            if not file_exists : 
                writer.writerow(HEADER)

            writer.writerow([date,currentTime,name,price])
        time.sleep(20)
        # print(time.now())


except requests.exceptions.RequestException as e:
    print("Error:", e)