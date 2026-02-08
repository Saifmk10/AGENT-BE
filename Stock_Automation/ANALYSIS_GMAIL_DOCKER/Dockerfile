FROM python:3.12-slim

WORKDIR /app

ARG REQUIREMENT_FILE=requirements.txt

COPY ${REQUIREMENT_FILE} /app/requirements.txt 

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python"]
