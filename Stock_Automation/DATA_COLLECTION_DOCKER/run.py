# entry point for fetchingStock.py
# any execution that needs to happen should happen here ONLY

import os


# ---- bootstrap config (GLOBAL) ----
BASE_DIR = os.getcwd()  # inside Docker this = /app

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "csvFiles",
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "reports",
)


def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


if __name__ == "__main__":
    # import AFTER runtime starts
    from Stock_price_fetching.fetchingStock import main

     # from Stock_Automation.ANALYSIS_GMAIL_DOCKER.collectedDataAnalysis import init_storage
    # from Stock_Automation.DATA_COLLECTION_DOCKER.fetchingStock import main

    # 1. ensure folders exist
    init_storage()

    # 2. start fetching
    main()
