import requests
from xml.etree import ElementTree as ET

def trendingNews(numberOfArticles):
    url = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.ok:
        try:
            root = ET.fromstring(response.content)
            channel = root.find("channel")
            items = channel.findall("item")

            articles = []
            for item in items[:numberOfArticles]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()

                if title and link:
                    articles.append({
                        "headline": title,
                        "link": link
                    })

            return {"news": articles}

        except Exception as e:
            return {"error": str(e)}

    return {"error": f"Request failed with status {response.status_code}"}


# result = trending_news(200)
# print(result)
   