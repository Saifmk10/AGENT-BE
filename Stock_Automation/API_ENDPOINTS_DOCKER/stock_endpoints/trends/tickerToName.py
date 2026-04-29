import csv
import os

def stockName(csv_file=None):
    if csv_file is None:
        csv_file = os.path.join(os.path.dirname(__file__), "EQUITY_L.csv")
    name_map = {}

    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                symbol = row.get("SYMBOL", "").strip()
                name = row.get("NAME OF COMPANY", "").strip()

                if symbol:
                    name_map[symbol] = name

    except Exception as e:
        print(f"Error loading CSV: {e}")

    return name_map