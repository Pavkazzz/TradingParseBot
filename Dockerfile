FROM python:3.7-slim

WORKDIR app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git build-essential gcc && \
    apt-get clean && rm -fr /var/cache/apt/archives/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY trading_bot trading_bot

ENV PYTHONPATH "${PYTHONPATH}:./"
CMD [ "python", "./trading_bot/main.py", "--redis-url", "redis"]

