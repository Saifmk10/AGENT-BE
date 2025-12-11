import requests
import time , csv

url = "https://the-chat-app-api-git-main-saifmks-projects.vercel.app/api/searchedapi.py?symbol=YESBANK"

try : 
    while url :
        response = requests.get(url)
        print("response : " , response.status_code)
        print(response.json())

        currentTime = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        data = response.json()
        # print(price["stockPrice"])

        price = float(data["stockPrice"])
        name = data["stockName"]

        with open("/app/input.csv" , "a" , newline="") as f:
            writer = csv.writer(f)
            writer.writerow([currentTime , name ,price])
        
        time.sleep(10)


except requests.exceptions.RequestException as e:
    print("Error:", e)