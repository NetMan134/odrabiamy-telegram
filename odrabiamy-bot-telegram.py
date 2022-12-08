#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

# odrabiamy - login variables (stored in environment)
from os import getenv
ODRABIAMY_LOGIN = getenv('ODRABIAMY_LOGIN')
ODRABIAMY_PASS = getenv('ODRABIAMY_PASS')

# postgresql - login variables (stored in environment)
DATABASE_HOST = getenv('DB_ADDRESS')
DATABASE_USER = getenv('DB_USER')
DATABASE_PASSWORD = getenv('DB_PASS')
DATABASE_NAME = getenv('DB_NAME')
DATABASE_TABLE = getenv('DB_TABLE')
DATABASE_PORT = getenv('DB_PORT')

import logging

"""Check python-telegram-bot version"""
from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This script is not compatible with your current PTB version {TG_VER}."
        f"Please install python-telegram-bot~=20.04a"
    )

from telegram import (ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, JobQueue, MessageHandler, filters)
from io import BytesIO
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from PIL import Image
import psycopg2, base64, requests, json, time, threading

# enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TYPE_LINK, SELECT_BUTTON = range(2)

def get_odrabiamy_token(email, password):
    """Check odrabiamy login details/premium subscription and get token"""
    try:
        get_token = requests.post(url='https://odrabiamy.pl/api/v2/sessions',
            json=({"login": f"{email}", "password": f"{password}"})).content
        return_token = json.loads(get_token).get('data').get('token')
        return return_token
    except:
        logger.error("Incorrect login details for odrabiamy. (Or no internet connection?)")
        quit()

# odrabiamy_token = get_odrabiamy_token(ODRABIAMY_LOGIN, ODRABIAMY_PASS)
odrabiamy_token = get_odrabiamy_token(ODRABIAMY_LOGIN, ODRABIAMY_PASS)

<<<<<<< Updated upstream
=======

# whitelist
def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user = update.message.from_user
        user_id = update.effective_user.id
        WHITELIST = []
        with open('whitelist.txt') as input_data:
            for num in input_data.readlines():
                try:
                    WHITELIST.append(int(num.split()[0]))
                except ValueError:
                    pass
        if user_id not in WHITELIST:
            logger.info("Unauthorized - ID: %s, Name: %s, Username: @%s).", user_id, user.first_name, user.username)
            await update.message.reply_text(f"Skontaktuj się z administratorem bota\ni podaj mu to ID: `{user_id}`\na jeśli go nie znasz \- nie powinno Cię tu być ;\)", parse_mode='MarkdownV2')
            return
        return await func(update, context, *args, **kwargs)
    return wrapped


>>>>>>> Stashed changes
def get_from_db(chosen_book_id, chosen_page_no):
    """Get content and exercises from a local PostgreSQL database"""
    psql_connection = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, host=DATABASE_HOST, password=DATABASE_PASSWORD, port=DATABASE_PORT)
    psql_cursor = psql_connection.cursor()
    psql_cursor.execute("SELECT content FROM {}\
                    WHERE book_id={} AND page_no={};".format(DATABASE_TABLE ,chosen_book_id, chosen_page_no))
    fetched_data = str(psql_cursor.fetchall())
    psql_cursor.execute("SELECT exercises FROM {}\
                    WHERE book_id={} AND page_no={};".format(DATABASE_TABLE, chosen_book_id, chosen_page_no))
    exercises_data = str(psql_cursor.fetchall())
    content = fetched_data.lstrip('[(\'').rstrip('\',)]')
    exercises_list = exercises_data.lstrip('[(\'').rstrip('\',)]')
    if content == "":
        logger.info("book_id: %s with page_no %s not present in database).", chosen_book_id, chosen_page_no)
    psql_cursor.close(); psql_connection.close()
    return content, exercises_list

def page_download(downloaded_book_id, downloaded_page_no):
    """Download page solution and insert it into PostgreSQL database"""
    page_data = json.loads(requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{downloaded_page_no}/{downloaded_book_id}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {odrabiamy_token}'})\
        .content.decode('utf-8')).get('data')
    downloaded_book_name = page_data[0]['book']['name']
    sum_of_exercises = active_exercise = 0
    list_of_exercise_ids = []
    list_of_exercise_nos = []
    for exercise in page_data:
        sum_of_exercises += 1
    page_html = f'<head><meta charset="UTF-8"></head><h1 style=\'font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\'>{downloaded_book_name}</h1>'
    while active_exercise < sum_of_exercises:
        active_exercise_no = page_data[active_exercise]['number']
        active_exercise_id = page_data[active_exercise]['id']
        list_of_exercise_ids.append(str(active_exercise_id)); list_of_exercise_nos.append(str(active_exercise_no))
        active_exercise_solution = BeautifulSoup(page_data[active_exercise]['solution'], 'html.parser')
        # page - remove duplicate svg objects
        for svg_class_small in active_exercise_solution.find_all('object', class_='small', type='image/svg+xml'):
            svg_class_small.extract()
        for svg_math_class_small in active_exercise_solution.find_all('object', class_='math small', type='image/svg+xml'):
            svg_math_class_small.extract()
        # add exercises information to page
        page_html += f'<div class="exercise-{active_exercise_id}"><h1 style=\'font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\'>Zadanie {active_exercise_no}, Strona {downloaded_page_no}</h1>{active_exercise_solution}</div><br>'
        active_exercise += 1
    page_html_with_base64_imgs = BeautifulSoup(page_html, 'html.parser')
    for img in page_html_with_base64_imgs.find_all('img'):
        data = img['src']
        image = requests.get(data)
        base64_image = base64.b64encode(image.content).decode('utf-8')
        page_html_with_base64_imgs.find('img', src=data)['src'] = 'data:image/jpeg;base64,{}'.format(base64_image)
    page_html_apostrophes = str(page_html_with_base64_imgs).replace('\'', '\'\'')
    str_list_of_ex_id = str(list_of_exercise_ids).replace('\'', '\"')
    str_list_of_ex_no = str(list_of_exercise_nos).replace('\'', '\"')
    psql_connection = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, host=DATABASE_HOST, password=DATABASE_PASSWORD)
    psql_cursor = psql_connection.cursor()
    psql_cursor.execute("DELETE FROM {} WHERE book_id={} AND page_no={};".format(DATABASE_TABLE, downloaded_book_id, downloaded_page_no))
    psql_cursor.execute("INSERT INTO {} VALUES ({}, {}, \'{} -separator- {}\', \'{}\');".format(DATABASE_TABLE, downloaded_book_id, downloaded_page_no, str_list_of_ex_id, str_list_of_ex_no, page_html_apostrophes))
    psql_connection.commit(); psql_cursor.close(); psql_connection.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Encourages to send odrabiamy link, waits 60 seconds for it, then - times out (timeout specified in main())"""
    user = update.message.from_user
    logger.info("User %s (@%s, id: %s) started the conversation (waiting 60s for a link).", user.first_name, user.username, user.id)
    await update.message.reply_text("Wklej link do odrabiamy (czekam 60 sekund)")

    return TYPE_LINK


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses list of exercises from specified page and displays button options for them"""
    user = update.message.from_user
    global chosen_book_name
    try:
        sent_url = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        chosen_book_id = sent_url[2].split('-')[1]
        get_book = requests.get(url=f'https://odrabiamy.pl/api/v3/books/{chosen_book_id}').content.decode('utf-8')
        if json.loads(get_book).get('name') == None:
            await update.message.reply_text('Nie ma takiej książki, spróbuj ponownie')
            await update.message.reply_text("Wklej link do odrabiamy (czekam 60 sekund)")
            logger.info("User %s (@%s, id: %s) typed wrong book, (waiting 60s for a link).", user.first_name, user.username, user.id)
            return TYPE_LINK
        chosen_book_name = str(json.loads(get_book).get('name'))
        try:
            chosen_page_no = sent_url[3].split('-')[1]
        except IndexError:
            chosen_page_no = json.loads(get_book)['pages'][0]
        if int(chosen_page_no) in json.loads(get_book)['pages']:
            pass
        else:
            await update.message.reply_text('Nie ma takiej strony, spróbuj ponownie')
            await update.message.reply_text("Wklej link do odrabiamy (czekam 60 sekund)")
            logger.info("User %s (@%s, id: %s) typed wrong page, (waiting 60s for a link).", user.first_name, user.username, user.id)
            return TYPE_LINK
    except IndexError:
        await update.message.reply_text('Niepoprawny adres URL')
        await update.message.reply_text("Wklej link do odrabiamy (czekam 60 sekund)")
        logger.info("User %s (@%s, id: %s) typed wrong link, (waiting 60s for a link).", user.first_name, user.username, user.id)
        return TYPE_LINK

    await update.message.reply_text(
        "Pobieranie listy zadań..."
    )

    db_exercises_list = get_from_db(chosen_book_id, chosen_page_no)[1]

    if db_exercises_list == "":
        logger.info("User %s (@%s, id: %s) - downloading list of exercises.", user.first_name, user.username, user.id)
        page_no_premium = json.loads(requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/{chosen_page_no}/{chosen_book_id}',
            headers={'user-agent':'new_user_agent-huawei-144'})\
            .content.decode('utf-8')).get('data')
        list_of_exercises = []
        list_of_exercise_ids = []
        for exercise in page_no_premium:
            list_of_exercise_ids.append(str(exercise['id']))
            list_of_exercises.append(str(exercise['number']))
    else:
        exercise_data = db_exercises_list.split("-separator-", 2)
        list_of_exercises = exercise_data[1].replace('[', '').replace(']', '').replace('\"', '').strip().split(',')
        list_of_exercise_ids = exercise_data[0].replace(' ', '').replace('[', '').replace(']', '').replace('\"', '').strip().split(',')

    def build_menu(buttons, columns, header_buttons = None, footer_buttons = None):
        menu = [buttons[i:i + columns] for i in range(0, len(buttons), columns)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu
    button_list = []
    a = 0
    for each in list_of_exercises:
        button_list.append(InlineKeyboardButton(each, callback_data = str(list_of_exercise_ids[a]) + " {} {} {}".format(chosen_book_id, chosen_page_no, str(each))))
        a += 1
    button_list.append(InlineKeyboardButton('split', callback_data = 'split' + " {} {}".format(chosen_book_id, chosen_page_no)))
    button_list.append(InlineKeyboardButton('all', callback_data = 'all' + " {} {}".format(chosen_book_id, chosen_page_no)))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, columns = 3))
    await update.message.reply_text(
        "Wybierz zadanie",
        reply_markup = reply_markup
    )
    logger.info("User %s (@%s, id: %s) - waiting for button response.", user.first_name, user.username, user.id)
    return SELECT_BUTTON


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    user = update.callback_query.from_user
    query = update.callback_query
    await query.answer()

    chosen_exercise_id = query.data.split(' ')[0]
    try:
        chosen_exercise_no = query.data.split(' ')[3]
    except IndexError:
        chosen_exercise_no = None
    chosen_book_id = query.data.split(' ')[1]
    chosen_page_no = query.data.split(' ')[2]
    if chosen_exercise_no == None:
        await query.edit_message_text(text=f"Wybrano: {chosen_exercise_id}")
    else:
        await query.edit_message_text(text=f"Wybrano: {chosen_exercise_no}")


    clean_data = get_from_db(str(chosen_book_id), str(chosen_page_no))[0]
    if clean_data == "":
        logger.info("User %s (@%s, id: %s) - requesting download from odrabiamy.", user.first_name, user.username, user.id)
        page_download(str(chosen_book_id), str(chosen_page_no))
        clean_data = get_from_db(str(chosen_book_id), str(chosen_page_no))[0]
        request_or_local = 'R'
    else:
        logger.info("User %s (@%s, id: %s) - opening from a local database.", user.first_name, user.username, user.id)
        request_or_local = 'L'
    clean_data = clean_data.replace('\\\'', '\'')
    soupFromFile = BeautifulSoup(clean_data, 'html.parser')
    
    if chosen_exercise_id != 'split':
        if chosen_exercise_id == 'all':
            getFileContents = str(soupFromFile)
            logger.info("User %s (@%s, id: %s) - capturing (all).", user.first_name, user.username, user.id)
        else:
            getFileContents = f'<head><meta charset="UTF-8"></head><h1 style=\'font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\'>{chosen_book_name}</h1>'
            getFileContents += str(soupFromFile.find('div', class_=f'exercise-{chosen_exercise_id}').extract())
            logger.info("User %s (@%s, id: %s) - capturing (exercise_id: %s).", user.first_name, user.username, user.id, chosen_exercise_id)
        getFileContents = getFileContents.replace('\'\'', "\'")
        page_html_clean = str(getFileContents.replace('\\xa0', '\\xc2\\xa0').encode("utf-8"))\
                            .replace('\\\\', '\\')\
                            .encode().decode('unicode-escape')\
                            .encode('raw-unicode-escape').decode()\
                            .lstrip('b\'').rstrip('\'')

        async def split_exercises_run(playwright):
            chromium = playwright.firefox
            browser = await chromium.launch()
            page = await browser.new_page()
            await page.set_content('{}'.format(page_html_clean))
            await page.wait_for_load_state('domcontentloaded')
            finalPngOutput = await page.screenshot(full_page=True)
            imgdata = Image.open(BytesIO(finalPngOutput)).size[1]
            await browser.close()
            return finalPngOutput, imgdata
        async with async_playwright() as playwright:
            playwright_output = await split_exercises_run(playwright)
        finalPngOutput = playwright_output[0]
        imgheight = playwright_output[1]
        if imgheight > 3000: document_or_picture = 'd'
        else: document_or_picture = 'p'
        if document_or_picture == 'd':
            await context.bot.send_document(update.effective_chat.id,
                BytesIO(finalPngOutput),filename=f"{request_or_local}_ALL_{chosen_book_name}_Strona_{chosen_page_no}.png")
        elif document_or_picture == 'p':
            await context.bot.send_photo(update.effective_chat.id,
                BytesIO(finalPngOutput),filename=f"{request_or_local}_SPLIT_{chosen_book_name}_Strona_{chosen_page_no}.png")

        if chosen_exercise_id == 'all': logger.info("User %s (@%s, id: %s) - sent (all).", user.first_name, user.username, user.id)
        else: logger.info("User %s (@%s, id: %s) - sent (exercise_id: %s).", user.first_name, user.username, user.id, chosen_exercise_id)
    else:
        ex_p_data = json.loads(requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/{chosen_page_no}/{chosen_book_id}',
            headers={'user-agent':'new_user_agent-huawei-144'})\
            .content.decode('utf-8')).get('data')
        list_of_exercise_ids = []
        for exercise in ex_p_data:
            list_of_exercise_ids.append(str(exercise['id']))
        for exercise in list_of_exercise_ids:
            getFileContents = f'<head><meta charset="UTF-8"></head><h1 style=\'font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\'>{chosen_book_name}</h1>'
            getFileContents += str(soupFromFile.find('div', class_=f'exercise-{exercise}').extract())
            getFileContents = getFileContents.replace('\'\'', "\'")
            page_html_clean = str(getFileContents.replace('\\xa0', '\\xc2\\xa0').encode("utf-8"))\
                                .replace('\\\\', '\\')\
                                .encode().decode('unicode-escape')\
                                .encode('raw-unicode-escape').decode()\
                                .lstrip('b\'').rstrip('\'')
            
            logger.info("User %s (@%s, id: %s) - capturing (split).", user.first_name, user.username, user.id)
            async def split_exercises_run(playwright):
                chromium = playwright.firefox
                browser = await chromium.launch()
                page = await browser.new_page()
                await page.set_content('{}'.format(page_html_clean))
                await page.wait_for_load_state('domcontentloaded')
                finalPngOutput = await page.screenshot(full_page=True)
                imgdata = Image.open(BytesIO(finalPngOutput)).size[1]
                await browser.close()
                return finalPngOutput, imgdata
            async with async_playwright() as playwright:
                playwright_output = await split_exercises_run(playwright)
            finalPngOutput = playwright_output[0]
            imgheight = playwright_output[1]
            if imgheight > 3000: document_or_picture = 'd'
            else: document_or_picture = 'p'
            if document_or_picture == 'd':
                await context.bot.send_document(update.effective_chat.id,
                    BytesIO(finalPngOutput),filename=f"{request_or_local}_ALL_{chosen_book_name}_Strona_{chosen_page_no}.png")
            elif document_or_picture == 'p':
                await context.bot.send_photo(update.effective_chat.id,
                    BytesIO(finalPngOutput),filename=f"{chosen_book_name}_{request_or_local}-SPLIT_Strona_{chosen_page_no}.png")
        logger.info("User %s (@%s, id: %s) - sent (split).", user.first_name, user.username, user.id)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    user = update.message.from_user
    logger.info("User %s (@%s, id: %s) requested help menu.", user.first_name, user.username, user.id)
    await update.message.reply_text("Użyj /start, następnie wyślij link do odrabiamy")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s (@%s, id: %s) canceled the conversation.", user.first_name, user.username, user.id)
    await update.message.reply_text(
        "Anulowanie", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# refresh odrabiamy token
async def refresh_token(update: Update) -> None:
    global odrabiamy_token
    odrabiamy_token = get_odrabiamy_token(ODRABIAMY_LOGIN, ODRABIAMY_PASS)
    logger.info("Refreshed odrabiamy token.")

def main() -> None:
    """Run the bot."""
    # create the Application and pass it your bot's token.

    async def post_init(application: Application) -> None:
        commands = [
            ("start", "Start"),
            ("pomoc", "Pomoc"),
            ("help", "Pomoc"),
            ("anuluj", "Anuluj"),
            ("cancel", "Anuluj"),
            ("stop", "Anuluj"),
        ]
        await application.bot.set_my_commands(commands)
    application = Application.builder().token(getenv("TG_TOKEN")).post_init(post_init).build()

    # refresh odrabiamy token every X seconds, 1728000 seconds (20 days) by default
    application.job_queue.run_repeating(callback=refresh_token, interval=1728000, first=0.0)

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler("start", start)],
        states = {
            TYPE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link)],
            SELECT_BUTTON: [CallbackQueryHandler(button)],
        },
        fallbacks = [
            CommandHandler("cancel", cancel),
            CommandHandler("anuluj", cancel),
            CommandHandler("stop", cancel),
        ],
        conversation_timeout = 60,
    )
    conv_handler.check_update(update=Update)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("pomoc", help_command))

    # run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
