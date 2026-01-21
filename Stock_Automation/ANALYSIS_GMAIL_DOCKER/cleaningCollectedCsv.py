import os
from pathlib import Path

#this will fetch the path where the csv file are added to [NOTE] : change the path if the file path has been changed
PATH_ACCESS = "/home/saifmk10/AGENT-DATA/Stock-Data/csvFiles/"





# function will be fetching all the files that are added into the analysis on a daily basis , this provides the data to the function bellow whicch is reposnsible for keeping the folder clean
def accessingData():
    returnedFinalpath = []
    userGmailFile = []


    # this will list all the user email that are being were added into the path as part of the analysis
    listedUserEmail = os.listdir(PATH_ACCESS)
    # print(listed)
    # returnedFinalpath = []

    if os.path.exists(PATH_ACCESS):
        try : 
            for file in listedUserEmail:
                print("USER EMAIL AS SAVED :",file)
                usersPath = os.path.join(PATH_ACCESS , file) #this will create the path of each user so the csv for each user can be accessed
                # print("-----------> USER PATH" , usersPath)
                fileContent = os.listdir(usersPath) # this will fetch all the file content in form od a list 
                # print("CONTENT LIST:",fileContent)
                

            

                # finds all the folders individually will no be used now , maybe later in the future development 
                for stockCsv in fileContent:
                    # print(stockCsv)
                    finalPath = os.path.join(usersPath , stockCsv) # the fetched in the list format is then split into individial stock name
                    
                    # print("FINAL PATH TO ACCESS : " , finalPath)
                    returnedFinalpath.append(finalPath)
                userGmailFile.append(usersPath)
            return returnedFinalpath , userGmailFile

        except OSError as error:
            print("ERROR IN DATA_CLEANSING_DOCKER [ERROR] :" , error)
        except OSError as error:
            print("ERROR IN DATA_CLEANSING_DOCKER [ERROR] :" , error)

# print(accessingData())


# handles the deletion of the files and also the deletion of the user folders that was created under the user email
def cleaningData():
    userDataPath , userDataFilePath = accessingData()


    if userDataFilePath :
        try:

            for path in userDataPath:
                print("Final Paths",path)
                os.remove(path)
                print("----------> CSV FILE DELETED :", path)
    
    
            for userDir in userDataFilePath:
                print("-----------> USER FOLDER DELETED :" , userDir)
                os.rmdir(userDir)
        except OSError as error:
            print("ERROR IN REMOVING USER DATA [ERROR]:" , error)
        except Exception as error:
            print("ERROR IN REMOVING USER DATA [ERROR]:" , error)

    # print(userDataPath[1])

    
    # print("----------> FILE DELETED",removeCsv)

# cleaningData()