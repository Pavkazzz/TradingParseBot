import asyncio
import logging
import ssl

from aiohttp import web
from aiotg import Bot

from trading_bot.settings import dev_hooks_token, chatbase_token, proxy_string

log = logging.getLogger(__name__)

bot = Bot(
    api_token=dev_hooks_token,
    chatbase_token=chatbase_token,
    name='TradingNewsBot',
    proxy=proxy_string
)


@bot.command(r"/echo (.+)")
def echo(chat, match):
    log.info('Incoming message %r', chat)
    return chat.reply(match.group(1))


SSL_CERT = '../YOURPUBLIC.pem'
SSL_PRIV = '../YOURPRIVATE.key'

# SSL_CERT = "../certificate.pem"
# SSL_PRIV = "../private.key"

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    port = 80
    host = '95.84.135.88'
    print(loop.run_until_complete(bot.api_call('getWebhookInfo')))

    print(ssl.OPENSSL_VERSION)

    webhook_future = bot.set_webhook(
        webhook_url=f'{host}:{port}/webhook/{dev_hooks_token}',
        certificate=open(SSL_CERT, 'rb')
    )
    loop.run_until_complete(webhook_future)
    app = bot.create_webhook_app(f'/webhook/{dev_hooks_token}', loop)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.load_cert_chain(SSL_CERT, SSL_PRIV)
    web.run_app(app, host='0.0.0.0', port=port, ssl_context=context)
