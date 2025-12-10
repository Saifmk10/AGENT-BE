import pandas as pd

data = pd.read_csv("input.csv")

print("STOCK PRICE FILTERED :")

def cleaningData ():

    # the data gets filtered by the name 
    filteredDataByName = data[
        
        data["STOCK_NAME"] == "REDINGTON"
    ]
    print(filteredDataByName)


    # conveting the string data into a time stamp
    data["EXTRACTED_TIME"] = pd.to_datetime(data["EXTRACTED_TIME"])


    # the data gets filtered according to that particular date
    filteredDataByDate = data[
        (data["STOCK_NAME"] == "REDINGTON") & (data["EXTRACTED_TIME"].dt.date == pd.to_datetime("2025-11-21").date())
    ]
    print(filteredDataByDate)


    # here as of now we have 3 segments of the data collected in 1 min which needs to be organized , in realworld we wont need
    filterDataByMin = (data.set_index("EXTRACTED_TIME").groupby("STOCK_NAME").resample("1min")["EXTRACTED_PRICE"].mean().reset_index())
    print(filterDataByMin.info())
    filterDataByMin.to_csv("input.csv" , index=False)


cleaningData ()