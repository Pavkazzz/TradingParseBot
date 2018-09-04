FROM python:3

WORKDIR app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY trading_bot trading_bot

ENV PATH="./trading_bot:${PATH}"
CMD [ "python", "./trading_bot/telegram_bot.py" ]

