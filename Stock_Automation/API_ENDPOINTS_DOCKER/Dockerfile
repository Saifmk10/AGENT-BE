FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt . 
RUN pip install -r requirements.txt

# expose the port in run time
# docker run -d -p 1555:1555 a8f934453b65

COPY . .

CMD ["uvicorn" , "main:app" , "--host" , "0.0.0.0" , "--port" , "1555"]