from telegram import Update, User
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import subprocess
import functools
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

TOKEN = os.getenv("TOKEN")
EBID= os.getenv("EBID")
ADID= os.getenv("ADID")

def with_auth(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print("Checking Auth")
        if str(args[0].effective_user.id) in [EBID,ADID]:
            user = await func(*args, **kwargs)
        else:   
            await args[0].message.reply_text(f'User Not Authenticated')

    return wrapper

async def hello(update: Update,context : ContextTypes.DEFAULT_TYPE) -> User:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    await update.message.reply_text(update.effective_user.id)
    return update.effective_user

@with_auth
async def printer(update:Update,context: ContextTypes.DEFAULT_TYPE) -> None:
    document = await update.message.document.get_file()
    file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")+document.file_path.split("/")[-1]
    accepted_extensions = ['jpg','jpeg','png','txt','pdf'] 
    file_ext = file_name.split(".")[-1] 
    file_save_path =f"./uploads/{file_name}" 
    if file_ext in accepted_extensions:
        print(str(datetime.now())+" : "+"Printing Media"+file_name)
        await update.message.reply_text(f"Printer is printing") 
        await document.download_to_drive(custom_path=file_save_path)
        subprocess.call(['lpr',file_save_path])
    elif file_ext in ['docx','doc']:
        print(str(datetime.now())+" : "+"Converting Media to PDF - "+file_name)
        await update.message.reply_text(f"Converting to PDF") 
        await document.download_to_drive(custom_path=f"./uploads/{file_name}")
        li = file_save_path.rsplit(file_ext,1)
        new_save_path = 'pdf'.join(li)
        subprocess.call(['libreoffice','--convert-to','pdf','--outdir','./uploads',file_save_path])
        await update.message.reply_text("Converted to PDF. Now Printing")
        return_value = subprocess.call(['lpr',new_save_path])

        print(return_value,new_save_path,file_save_path)
        await update.message.reply_text("Printed")

    else:
        await update.message.reply_text("Extension not supported")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(MessageHandler(filters.Document.ALL, printer))
app.run_polling(allowed_updates=Update.ALL_TYPES)

