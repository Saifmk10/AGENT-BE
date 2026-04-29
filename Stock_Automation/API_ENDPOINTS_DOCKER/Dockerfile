# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt . 
# RUN pip install -r requirements.txt

# # expose the port in run time
# # docker run -d -p 1555:1555 a8f934453b65

# COPY . .

# # Use PORT env variable if set (Railway will set this), otherwise default to 1555 (local)
# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-1555}"]





# use for prod


FROM python:3.11-slim

WORKDIR /app

# use full path from repo root
COPY Stock_Automation/API_ENDPOINTS_DOCKER/requirements.txt .
RUN pip install -r requirements.txt

# copy only your service, not entire repo
COPY Stock_Automation/API_ENDPOINTS_DOCKER/ .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-1555}"]