FROM python:3

WORKDIR app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY trading_bot trading_bot

ENV PYTHONPATH "${PYTHONPATH}:./"
CMD [ "python", "./trading_bot/async_webserver.py", "--redis-url", "redis"]

