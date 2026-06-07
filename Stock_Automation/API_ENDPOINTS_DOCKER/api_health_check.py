import requests


gainer_checker = requests.get("http://0.0.0.0:1555/gainer?limit=5")

loser_checker = requests.get("http://0.0.0.0:1555/loser?limit=5")

most_active_checker = requests.get("http://0.0.0.0:1555/mostActive?limit=5")

search_checker = requests.get("http://0.0.0.0:1555/search/REDIGNTON")


def messager (message_to_send):
    requests.post("https://ntfy.sh/api-health",data=message_to_send.encode(encoding='utf-8'))


if gainer_checker.status_code == 200 and gainer_checker.json().get("trending_stocks") and len(gainer_checker.json().get("trending_stocks")) > 0:
    messager("Gainer endpoint is working fine.")
else:
    messager(f"Gainer endpoint is not working fine. Status code: {gainer_checker.status_code}, Response: {gainer_checker.text}")

if loser_checker.status_code == 200 and loser_checker.json().get("trending_stocks") and len(loser_checker.json().get("trending_stocks")) > 0:
    messager("Loser endpoint is working fine.")
else:
    messager(f"Loser endpoint is not working fine. Status code: {loser_checker.status_code}, Response: {loser_checker.text}")

if most_active_checker.status_code == 200 and most_active_checker.json().get("trending_stocks") and len(most_active_checker.json().get("trending_stocks")) > 0:
    messager("Most Active endpoint is working fine.")
else:
    messager(f"Most Active endpoint is not working fine. Status code: {most_active_checker.status_code}, Response: {most_active_checker.text}")

if search_checker.status_code == 200 and search_checker.json().get("stock_price") and search_checker.json().get("stock_price").get("ticker") == "REDIGNTON":    
    messager("Search endpoint is working fine.")
else:    
    messager(f"Search endpoint is not working fine. Status code: {search_checker.status_code}, Response: {search_checker.text}")
    


# print(gainer_checker.status_code)
# print(loser_checker.text)
# print(most_active_checker.text)
# print(search_checker.text)

