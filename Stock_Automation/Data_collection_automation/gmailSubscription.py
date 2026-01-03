# this module plays the main role where the mail is send to the user with the report on a daily basis as of now , 
#in this module we cal the fn that is responsible for converting the csv into a useful html that will later be sned to the user

import yagmail
import collectedDataAnalysis
import os

# all the base dir that will be used during the automation
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(
    BASE_DIR,
     "Data_collection_automation",
     "Analysed_Files_data",
     "reports", 
)
users = os.listdir(REPORT_DIR)

# calling the function that makes sure all the data is parsed into a html format and ready to be send as mail
collectedDataAnalysis.mailParser()

# all the gamil requirements needed to send the mail to all the listed users
yag = yagmail.SMTP('saifmohasaif216@gmail.com' , 'lefw fwqi eqnp lvvb') 
gmail = []
content = ""


# for loop that looks into the rerport repo and fetch all the user email and also the data that has been provided for each other
for userEmail in users:
    USERS_DIR = os.path.join(REPORT_DIR , userEmail)
    # print(userEmail)
    finalReport = os.listdir(USERS_DIR)
    # print(finalReport[0])
    REPORT_FILES = os.path.join(USERS_DIR , finalReport[0])

    with open(REPORT_FILES , "r" , encoding="utf-8") as file:
        data = file.read()

    # print(data)

    content = data
    gmail.append(userEmail)
    


print(gmail)


subject = "Daily stock price analysis summary"

try : 
    yag.send(gmail , subject , content)
    print(f"MAIL SENT TO {gmail}")
except Exception as error : 
    print(f"ERROR IN AUTHENTICATION : {error}")



