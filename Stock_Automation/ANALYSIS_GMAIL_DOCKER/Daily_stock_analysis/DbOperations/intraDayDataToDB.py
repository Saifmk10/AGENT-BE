import os
from connection import db
from firebase_admin import auth
# from google.api_core import exceptions
from  datetime import datetime
import pytz
import json

DATA_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/csvFiles"
REPORT_DIR = "/home/saifmk10/AGENT-SERVICES/AGENT-BE/test/reports"

# [NOTE] docker path used for prod only
# DOCKER_PATH = os.environ.get("DOCKER_PATH")
# DATA_DIR = os.path.join(DOCKER_PATH , "csvFiles")
# REPORT_DIR = os.path.join(DOCKER_PATH , "reports")


ist = pytz.timezone("Asia/Kolkata")
time = datetime.now(ist)
currentTime = time.strftime("%H:%M:%S")
todaysDate = time.strftime("%d-%m-%Y")

def fetchingUserAddedStock():

    # here the snapshot of the database is collected to all the access to the database can be done using this variable as the entry point
    documentSnapshot = (
        db.collection("Users")
        .stream()
    )

    userAddedStocks = []
    addedStock = []     #list gonna hold all the stock names a user has added
    # this is the entry point where all the data fetching is goonna start , the loop taken in all the uid and then puts it into the next checking availabilty path
    for doc in documentSnapshot:
        data = doc.to_dict()
        # print(data["UserId"])
        # userId = data["UserId"]
        userId = doc.id
        
        # userEmail = data["Email"]
        userEmail = data.get("Email")
        # print("FIXED BD ERROR --->",userId , userEmail)

        # this is the var which is responsible for fetching if the user has a subscribed to use the stock agent , if they have subscribed then the data will the collected
        CheckAvailabilityPath = (
            db.collection("Users").document(userId).collection("Agents").document("Finance").get()
        )

        # If the user has subscribed then the next steps happens to fetch all the names of the stock ONLY
        if CheckAvailabilityPath.exists : 
            # print("data will be collected")
            
            fetchingStockNames = (
                db.collection("Users").document(userId).collection("Agents").document("Finance").collection("Stock_Added").stream()
            )
            # print(fetchingStockNames)

           
        
            # once the user is cinfirned to have a stock_added in the db then the stock will be fetched
            for stocks in fetchingStockNames:
                data = stocks.to_dict()
                # print(userEmail)
                # print(data["stockName"])
                addedStock.append(userEmail)

    
    # print(list(dict.fromkeys(addedStock)))

    # print(addedStock)
    return list(dict.fromkeys(addedStock))



def updatingIntrDay ():
    # print(DATA_DIR , REPORT_DIR)
    # REPORT_DIR
    # userEmail = os.listdir(REPORT_DIR)
    # print(userEmail)
    dbUserEmail = fetchingUserAddedStock()
    print(dbUserEmail)

    # the for loop takes all the emails present in the db , then the emails are joined to the path and of path exists file is extracted if not then ignored
    for email in dbUserEmail:
        try : 
            userEmailPath = os.path.join(REPORT_DIR , email)
            # print(userEmailPath)
            userJsonList = os.listdir(userEmailPath)
            # print(processedJson)

            # 
            for file in userJsonList:
                userDataPath = os.path.join(userEmailPath , file)
                print(userDataPath)
                
                if os.path.exists(userDataPath):

                    try :
                        with open(userDataPath , "r" , encoding="utf-8") as fileContent : 
                            content = fileContent.read()
                            jsonFormat = json.loads(content)


                        for day in jsonFormat["HISTORY"]:
                            if day["date"] == todaysDate:
                                dataForDate = day
                                print("UPDATED USER DATA WITH DATE " , dataForDate)
                                break

                        # data = dataForDate["report"]
                        data = {
                            "date": dataForDate["date"],
                            "report": dataForDate["report"],
                            "summary": dataForDate["summary"]
                        }
                    
                    except (FileNotFoundError, PermissionError, IsADirectoryError, UnicodeDecodeError, OSError):
                        print("ERROR READING DATA FROM FILES IN datatoDatabase.py , [ERROR]:" , error)



                    
                    userCred = auth.get_user_by_email(email)
                    uid = userCred.uid
                    print("UID --->" , userCred.uid)

                    try:
                        ref = (db.collection("Users").document(uid).collection("Agents").document("Finance").collection("Stock_Data").document("IntraDay").collection("Data").document(todaysDate))

                        ref.set({
                            "last_added" : currentTime, 
                            "DATA" : data
                        })

                        print("---> DATA ADDED INTO UID : " , uid)
                    # except ( PermissionDenied, NotFound, AlreadyExists, InvalidArgument, ResourceExhausted, DeadlineExceeded, Aborted, Unavailable )
                    except Exception as error :
                        print("ERROR IN FB -->" , error)


                # print(content)

        except (FileNotFoundError , IsADirectoryError , OSError ) as error : 
            print("file Error :" , error)
            continue

    

# print(data)
updatingIntrDay()
