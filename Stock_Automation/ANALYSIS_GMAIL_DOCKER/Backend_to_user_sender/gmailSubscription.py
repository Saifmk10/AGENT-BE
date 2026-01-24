# this module plays the main role where the mail is send to the user with the report on a daily basis as of now , 
#in this module we cal the fn that is responsible for converting the csv into a useful html that will later be sned to the user

import yagmail
import Stock_analysis_modules.collectedDataAnalysis as collectedDataAnalysis
from Backend_to_user_sender.mail_parser.mailParserModule import mailParser
import os
from Csv_path_cleaner.cleaningCollectedCsv import cleaningData

# USE this for local testing only , if tested locally change it to the test dir
# REPORT_DIR =  "/home/saifmk10/AGENT-DATA/Stock-Data/reports"

DOCKER_PATH = os.environ.get("DOCKER_PATH")
REPORT_DIR = os.path.join(DOCKER_PATH , "reports")

def main():

    # calling the function that makes sure all the data is parsed into a html format and ready to be send as mail
    mailParser()

    # all the gamil requirements needed to send the mail to all the listed users
    yag = yagmail.SMTP('saifmohasaif216@gmail.com' , 'lefw fwqi eqnp lvvb') 
    gmail = []
    content = ""

    users = os.listdir(REPORT_DIR)

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
        subject = "Daily stock price analysis summary"

        try : 
            yag.send(userEmail , subject , content)
            print(f"MAIL SENT TO {userEmail}")
            cleaningData()
        except Exception as error : 
            print(f"ERROR IN AUTHENTICATION : {error}")

    print(users)
