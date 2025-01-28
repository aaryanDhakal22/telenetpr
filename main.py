from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import functools
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
USER_ID = os.getenv("USER_ID")

def with_auth(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print("Checking Auth")
        if str(args[0].effective_user.id) == USER_ID :
            user = await func(*args, **kwargs)
        else:   
            await args[0].message.reply_text(f'User Not Authenticated')
        print(f"{user.username} is authenticated")
    return wrapper

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    return update.effective_user

@with_auth
async def printer(update:Update,context: ContextTypes.DEFAULT_TYPE) -> None:
    print("printing media")
    return update.effective_sender


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("print", print))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(MessageHandler(filters.Document.ALL, printer))
app.run_polling(allowed_updates=Update.ALL_TYPES)

