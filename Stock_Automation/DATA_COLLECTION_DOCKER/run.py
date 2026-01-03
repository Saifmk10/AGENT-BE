# entry point for the fetchinfStock.py as the paths were not working well this was added
#any execution thay need to happen on the fetchingStock.py needs to happen in this file ONLY

if __name__ == "__main__":
    # import ONLY after runtime starts
    from Stock_Automation.ANALYSIS_GMAIL_DOCKER.collectedDataAnalysis import init_storage
    from Stock_Automation.DATA_COLLECTION_DOCKER.fetchingStock import main

    # 1. ensure folders exist
    init_storage()

    # 2. start fetching
    main()