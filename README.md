# WebParserBot
Telegram bot for parsing web

# Todo: 
pass the telegram token throw env

silent mode at night 

improve caching

update message instead of sending new if data changes

after midnight site change today -> yesterday. mfd comments

# Requirements
- Python 3.7+

# Usage:
1) git clone git@github.com:Pavkazzz/WebParserBot.git TradingBot

2) cd TradingBot

3) python -m venv .

4) source bin/activate

5) pip install -U -r requirements.txt

6) docker build --no-cache -t telegram_bot .

7) docker run -d --rm -v $(pwd)/data:/app/data --name telegram_bot telegram_bot
