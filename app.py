from __future__ import print_function

import json
import logging
import os.path
import pickle
import time
import urllib
from functools import partial

import gspread
import redis
# from googleapiclient.http import MediaFileUpload
import shortuuid
import telegram.bot
from apiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)

import txt
from config import *

# constants
NAME, PHOTO, YEAR, AUTHOR, PLATFORM, LINK, CATEGORY = range(7)
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file'
          ]

# vars
data = {}

# initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# initialize google sheet
gc = gspread.service_account(filename=GOOGLE_CREDENTIALS)
gsheet = gc.open_by_url(SPREADSHEET)

# initialize database
r = redis.Redis()

# initialize bot
bot = telegram.Bot(TOKEN)


# authenticate to google drive
def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'drivecredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


# get json data from url (used to check number of db entries)
def getResponse(url):
    operUrl = urllib.request.urlopen(url)
    if (operUrl.getcode() == 200):
        data = operUrl.read()
        jsonData = json.loads(data)
    else:
        logger.info("Error receiving data %s", operUrl.getcode())
        jsonData = 'error'
    return jsonData


# save to redis database (we save accepted and discarded entries)
def save_to_db(data):
    r.hmset(data['id'], data)
    try:
        r.bgsave()
    except:
        pass
    logger.info("Meme %s saved to database", data['id'])
    return


# upload image to google drive
def upload_to_drive(id, image):
    file = bot.getFile(image)
    file.download('meme.jpg')
    service = get_gdrive_service()
    file_metadata = {
        "name": id,
        "parents": [FOLDER_ID]
    }
    # upload
    media = MediaFileUpload("meme.jpg", resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    logger.info("File saved to drive, id: %s", file.get("id"))
    return file.get("id")


# append accepted meme data to google spreadsheet
def append_to_gsheet(id):
    name = str(r.hget(id, 'name').decode('utf-8'))
    image = str(r.hget(id, 'image').decode('utf-8'))
    year = str(r.hget(id, 'year').decode('utf-8'))
    author = str(r.hget(id, 'author').decode('utf-8'))
    platform = str(r.hget(id, 'platform').decode('utf-8'))
    link = str(r.hget(id, 'link').decode('utf-8'))
    index_row = str(len(gsheet.sheet1.get_all_records()) + 2)
    drive_image_id = upload_to_drive(id, image)
    drive_url = "https://drive.google.com/open?id=" + drive_image_id
    category = str(r.hget(id, 'category').decode('utf-8'))
    data_list = [[id, name, drive_url, year, author, platform, link, category]]
    gsheet.sheet1.update('A' + index_row + ':H' + index_row, data_list)
    return print("saved to google sheet!")


# saves to google sheets
def save_meme(update, context, data):
    update.callback_query.answer()
    id = update.callback_query.message.caption.split("\n")[0]
    context.bot.edit_message_reply_markup(chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=None)
    append_to_gsheet(id)
    return


def discard(update, context):
    update.callback_query.answer()
    print("discarded")
    return context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)


# sends meme to control admins group for approval
def spam(data=data):
    button_list = [[InlineKeyboardButton("Save", callback_data="save_meme"),
                    InlineKeyboardButton("Discard", callback_data="discard")]]
    reply_markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)
    text = data['id'] + "\n\n" \
                        "Name: " + data['name'] + "\n" \
                                                  "Year: " + data['year'] + "\n" \
                                                                            "Author: " + data['author'] + "\n" \
                                                                                                          "Platform: " + \
           data['platform'] + "\n" \
                              "Link: " + data['link'] + "\n" \
                                                        "Category: " + data['category'] + "\n"
    bot.send_photo(chat_id=CHANNEL_ID, photo=data['image'], caption=text, reply_markup=reply_markup)


def start(update, context):
    data.clear()
    # print(data)
    update.message.reply_text(txt.start)
    return NAME


def name(update, context):
    user = update.message.from_user
    data['id'] = shortuuid.uuid()
    data['timestamp'] = str(time.time()).replace(".", "")
    data['name'] = update.message.text
    logger.info("Name of the meme sent by %s: %s", user.first_name, update.message.text)
    update.message.reply_text(txt.name)
    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].file_id
    data['image'] = photo_file
    # photo_file.download('meme.jpg')
    logger.info("Meme image: %s: %s", user.first_name, 'meme.jpg')
    update.message.reply_text(txt.photo)
    return YEAR


def year(update, context):
    user = update.message.from_user
    data['year'] = update.message.text
    logger.info("Year of %s's meme: %s", user.first_name, update.message.text)
    update.message.reply_text(txt.year)
    return AUTHOR


def skip_year(update, context):
    user = update.message.from_user
    data['year'] = ''
    logger.info("User %s did not send a year.", user.first_name)
    update.message.reply_text(txt.year)

    return AUTHOR


def author(update, context):
    user = update.message.from_user
    data['author'] = update.message.text
    logger.info("Year of %s's meme: %s", user.first_name, update.message.text)
    update.message.reply_text(txt.author)

    return PLATFORM


def skip_author(update, context):
    user = update.message.from_user
    data['author'] = ''
    logger.info("User %s did not send an author.", user.first_name)
    update.message.reply_text(txt.author)
    return PLATFORM


def platform(update, context):
    user = update.message.from_user
    data['platform'] = update.message.text
    logger.info("Platform of %s's meme: %s", user.first_name, update.message.text)
    update.message.reply_text(txt.platform)

    return LINK


def skip_platform(update, context):
    user = update.message.from_user
    data['platform'] = ''
    logger.info("User %s did not send a link.", user.first_name)
    update.message.reply_text(txt.platform)
    return LINK


def link(update, context):
    user = update.message.from_user
    data['link'] = update.message.text
    logger.info("Link of %s's meme: %s", user.first_name, update.message.text)
    update.message.reply_text(txt.link, reply_markup=ReplyKeyboardMarkup(categories_keyboard, one_time_keyboard=True))
    return CATEGORY


def skip_link(update, context):
    user = update.message.from_user
    data['link'] = ''
    logger.info("User %s did not send a link.", user.first_name)
    update.message.reply_text(txt.link, reply_markup=ReplyKeyboardMarkup(categories_keyboard, one_time_keyboard=True))
    return CATEGORY


def category(update, context):
    user = update.message.from_user
    data['category'] = update.message.text.split('.')[0]
    logger.info("Category of %s's meme: %s", user.first_name, data['category'])
    update.message.reply_text(txt.category)
    save_to_db(data)
    spam(data)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation. ", user.first_name)
    update.message.reply_text(txt.cancel)
    data.clear()
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],

            PHOTO: [MessageHandler(Filters.photo, photo)],

            YEAR: [MessageHandler(Filters.text & ~Filters.command, year),
                   CommandHandler('skip', skip_year)],

            AUTHOR: [MessageHandler(Filters.text & ~Filters.command, author),
                     CommandHandler('skip', skip_author)],

            PLATFORM: [MessageHandler(Filters.text & ~Filters.command, platform),
                       CommandHandler('skip', skip_platform)],

            LINK: [MessageHandler(Filters.text & ~Filters.command, link),
                   CommandHandler('skip', skip_link)],

            CATEGORY: [MessageHandler(Filters.text, category)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=360)

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(partial(save_meme, data=data), pattern="save_meme"))
    dp.add_handler(CallbackQueryHandler(discard, pattern="discard"))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
