import requests
from Stock_analysis_modules.collectedDataAnalysis import fetchCollectedData 



data = fetchCollectedData()
ollama_warmed = False

def ollamaResponse(data):
    global ollama_warmed
    #url = "http://localhost:11434/api/generate" #use for local testing
    url = "http://ollama:11434/api/generate" #container url works only for docker

    print("complete data : " , data)
    # runs the code once to prevent cold start
    if not ollama_warmed:
        try:
            requests.post(
                url,
                json={
                    "model": "phi3:mini",
                    "prompt": "OK",
                    "options": {
                        "num_predict": 1,
                        "temperature": 0
                    },
                    "stream": False
                },
                timeout=10
            )
        except Exception:
            pass
        ollama_warmed = True

    #prompt used to define the models task \
    #[NOTE] : update the prompt asper user requirement
    prompt = f"""

            Convert the stock analysis below into a short, easy-to-understand message for a normal user.
            Limit the response to 100 words.

            Stock analysis:
            {data}


            """

    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "options": {
            "num_predict": 100,
            "temperature": 0.2
        },
        "stream": False
    }

    try:
        res = requests.post(url, json=payload, timeout=120)
        text = res.json().get("response", "")
        return text
    except Exception as error:
        print(error)


def main():

    for userData in data :
        print("=====> USER DATA :" , userData)
        report = ollamaResponse(userData)
        print("---------> USER DATA ANALYSIS :" , report)