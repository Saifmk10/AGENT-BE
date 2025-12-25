# this file is responsible for fetching of all the stock names from the db
#it checks all the users and finds the users who have subscribed to the agent then only then fetch the data from the db
#once the data has been fetched the data will be then send to the logics reponsible for fetching the stock name and all the analysis
#once the stock has been fetched it is then added into the fuzzy logic where the stock name is matched with the token that the api can understand
# Data_fetching_from_db.
from Data_fetching_from_db.connection import db       #a file thay contains all the code for the connection to the db
import os , csv
from rapidfuzz import process, fuzz





#loading the tickers list from the cvs , only the loading of data and segrigation of data happens in this function
def loadTickerList():
    csvPath = os.path.join(os.path.dirname(__file__), "EQUITY_L.csv")

    ticker_list = []
    stock_dict = {}

    with open(csvPath, "r", encoding="utf-8") as dataset:
        reader = csv.DictReader(dataset)

        for row in reader:
            symbol = row.get("SYMBOL")
            company = row.get("NAME OF COMPANY")

            if symbol and company:
                symbol = symbol.strip().upper()
                company = company.strip()

                ticker_list.append(symbol)
                stock_dict[symbol] = company

    return ticker_list, stock_dict



# bellow code is for the fuzzy logic , where the code for fetching the data set has been placed so that the dataset is accessed only when called.
def fuzzyLogic(user_input, stock_dict, threshold=85):
    if not user_input or not stock_dict:
        return None

    company_names = list(stock_dict.values())

    match = process.extractOne(
        user_input,
        company_names,
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    matched_name, score, index = match

    if score < threshold:
        return None

    return list(stock_dict.keys())[index]





# function responsible for fetching all the stocks that a user has added to the db
def fetchingUserAddedStock():

    # here the snapshot of the database is collected to all the access to the database can be done using this variable as the entry point
    documentSnapshot = (
        db.collection("Users")
        .stream()
    )

    userAddedStocks = []

    # this is the entry point where all the data fetching is goonna start , the loop taken in all the uid and then puts it into the next checking availabilty path
    for doc in documentSnapshot:
        data = doc.to_dict()
        # print(data["UserId"])
        userId = data["UserId"]
        userEmail = data["Email"]

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

            addedStock = []     #list gonna hold all the stock names a user has added
        
            # once the user is cinfirned to have a stock_added in the db then the stock will be fetched
            for stocks in fetchingStockNames:
                data = stocks.to_dict()
                # print(userEmail)
                # print(data["stockName"])
                addedStock.append(data["stockName"])

            try:

                # if the user has met all the requirements as above and there are stock present in his collection then userAddedStocks will be returned for data fetching
                if addedStock :     
                    userAddedStocks.append (
                         {
                        "useremail" : userEmail, 
                        "stocks" : addedStock,
                        }
                    ) 
                    # print(userAddedStocks)
                    # return userAddedStocks 
            except Exception as error : 
                print("error in stock name fetching" , error)    
    
    
    # all the functions gets combined here and then the loaded adds the data into stockDict , the fuzzylogic appends the data into the list , the symbol list is the final output that will be delivered during the function
    tickerList, stockDict = loadTickerList()
    
    result = userAddedStocks
    finalResult = []
    
    # loops helping to read through the tuple and the list
    for userStock in result: 
        email = userStock["useremail"]
        stock = userStock["stocks"]

        symbol = [] #holds all the conversted stock names into symbols

        for stockName in stock:
            value = fuzzyLogic(stockName , stockDict)
            if value : 
                symbol.append(value)

        # parsing the final data into a dict format
        if symbol:
            finalResult.append({
                "email" : email,
                "stocks" : symbol
            })




    return finalResult
    

# debug only
# print(fetchingUserAddedStock())