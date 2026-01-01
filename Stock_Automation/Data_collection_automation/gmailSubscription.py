import yagmail
import collectedDataAnalysis
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(
    BASE_DIR,
     "Data_collection_automation",
     "Analysed_Files_data",
     "reports", 
)
users = os.listdir(REPORT_DIR)

collectedDataAnalysis.mailParser()

yag = yagmail.SMTP('saifmohasaif216@gmail.com' , 'lefw fwqi eqnp lvvb') 
gmail = []
content = ""



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


# this is currently a test code not stuctured properly so needs to be updated with addition of functions