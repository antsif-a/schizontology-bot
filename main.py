import asyncio, html, logging, traceback
import json
from os import environ as env
from telegram import Update, ChatFullInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler
from telegram.ext.filters import UpdateFilter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

replies = {
    'start': 'Предложка Шизоидной к вашим услугам!',
    'admin_schizo': 'Реально шиз? Иди пости мемы, пока админку не отобрали',
    'sent_ok': 'Ваш мем был отправлен на рассмотрение 👍',
    'error': 'Ашипка!'
}

async def get_notify_users(context: ContextTypes.DEFAULT_TYPE) -> list[ChatFullInfo]:
    return await asyncio.gather(*[context.bot.get_chat(i) for i in env['NOTIFY_CHAT_IDS'].split(':')])

async def get_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return update.effective_chat.username in [
        admin.user.username for admin in await context.bot.get_chat_administrators(env['CHANNEL_ID'])
    ]

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__, limit=3)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    await context.bot.send_message(
        chat_id=env['DEVELOPER_CHAT_ID'],
        text=(
            f'{replies['error']}\n'
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f'<pre>{html.escape(''.join(tb_list))}</pre>'
        ),
        parse_mode=ParseMode.HTML
    )

async def start_command_handler(update: Update, _):
    await update.message.reply_text(replies['start'])

class PersonalMessageFilter(UpdateFilter):
    def filter(self, update: Update) -> bool:
        return bool(update.message)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = replies['admin_schizo'] if await get_admin_users(update, context) else replies['sent_ok']
    await update.message.reply_text(reply)
    for user in await get_notify_users(context):
        await update.message.forward(user.id)

if __name__ == '__main__':
    app = ApplicationBuilder().token(env['TOKEN']).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler('start', start_command_handler))
    app.add_handler(MessageHandler(PersonalMessageFilter(), message_handler))
    app.run_polling()
