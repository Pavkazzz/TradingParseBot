FROM python:3.7-slim

WORKDIR app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git build-essential gcc libfreetype6-dev libjpeg-dev zlib1g-dev fontconfig && \
    apt-get clean && rm -fr /var/cache/apt/archives/*

RUN mkdir -p /usr/share/fonts/truetype/rmedium
COPY assets/rmedium.ttf /usr/share/fonts/truetype/rmedium
RUN fc-cache -f

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY trading_bot trading_bot

ENV PYTHONPATH "${PYTHONPATH}:./"
CMD [ "python", "./trading_bot/main.py"]

