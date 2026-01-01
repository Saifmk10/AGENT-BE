# entry point for the fetchinfStock.py as the paths were not working well this was added
#any execution thay need to happen on the fetchingStock.py needs to happen in this file ONLY

from Data_collection_automation.fetchingStock import main
from Data_collection_automation.collectedDataAnalysis import init_storage

if __name__ == "__main__":
    init_storage() 
    main()