import logging
from telegram.ext import Updater, CommandHandler
from settings import token
from database import addToDatabase
from Parser import newMessageCheck
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
updater = Updater(token)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('add', addToDatabase))
j = updater.job_queue
job_minute = j.run_repeating(newMessageCheck, interval=60, first=0)
updater.start_polling()
updater.idle()

