# WebParserBot
Telegram bot for parsing web

# Todo: 
pass the telegram token throw env

# Requirements
- Python 3.7+

# Usage:
1) git clone git@github.com:Pavkazzz/WebParserBot.git TradingBot

2) cd TradingBot

3) python -m venv .

4) pip install -U -r requirements.txt

5) docker build --no-cache -t telegram_bot .

6) docker run -d --rm -v $(pwd)/config.py/data:/app/data --name telegram_bot telegram_bot