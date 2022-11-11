import psycopg2, base64, requests, json
from playwright.sync_api import sync_playwright
from io import BytesIO
from os import getenv
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from bs4 import BeautifulSoup


# odrabiamy - login variables (stored in environment)
odrabiamy_login = getenv('ODRABIAMY_LOGIN')
odrabiamy_pass  = getenv('ODRABIAMY_PASS')

# telegram - bot token variables (stored in environment variable)
updater = Updater(
    getenv('TELEGRAM_BOT_TOKEN'),
use_context=True)

# postgresql - login variables (stored in environment)
DATABASE_HOST=getenv('DB_ADDRESS'); DATABASE_USER=getenv('DB_USER'); DATABASE_PASSWORD=getenv('DB_PASS'); DATABASE_NAME=getenv('DB_NAME')


# odrabiamy - check login details/premium subscription and get token
def get_odrabiamy_token(email, password):
    try:
        get_token = requests.post(url='https://odrabiamy.pl/api/v2/sessions',
            json=({"login": f"{email}", "password": f"{password}"})).content
        return_token = json.loads(get_token).get('data').get('token')
        return return_token
    except:
        print('\nIncorrect login details for odrabiamy.\nOr perhaps you don\'t have premium?\n(Or no internet connection?)')
        quit()

# odrabiamy - assign token
odrabiamy_token = get_odrabiamy_token(odrabiamy_login, odrabiamy_pass)

# odrabiamy - download page
def page_download():
    global book_name, active_exercise_no, page_html, DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, book_id, page_no, page_html_with_base64_imgs
    page_data = json.loads(requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page_no}/{book_id}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {odrabiamy_token}'})\
        .content.decode('utf-8')).get('data')
    sum_of_exercises = active_exercise = 0
    for exercise in page_data:
        sum_of_exercises += 1
    page_html = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\">{book_name}</h1>'
    while active_exercise < sum_of_exercises:
        active_exercise_no = page_data[active_exercise]['number']
        active_exercise_id = page_data[active_exercise]['id']
        active_exercise_solution = BeautifulSoup(page_data[active_exercise]['solution'], 'html.parser')
        # page - delete duplicate svg objects
        for svg_class_small in active_exercise_solution.find_all('object', class_='small', type='image/svg+xml'):
            svg_class_small.extract()
        for svg_math_class_small in active_exercise_solution.find_all('object', class_='math small', type='image/svg+xml'):
            svg_math_class_small.extract()
        # add active exercise to full html page
        page_html += f'<div class="exercise-{active_exercise_id}"><h1 style=\"font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\">Zadanie {active_exercise_no}, Strona {page_no}</h1>{active_exercise_solution}</div><br>'
        active_exercise += 1
    page_html_with_base64_imgs = BeautifulSoup(page_html, 'html.parser')
    for img in page_html_with_base64_imgs.find_all('img'):
        data = img['src']
        image = requests.get(data)
        base64_image = base64.b64encode(image.content).decode('utf-8')
        page_html_with_base64_imgs.find('img', src=data)['src'] = 'data:image/jpeg;base64,{}'.format(base64_image)
    psql_connection = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, host=DATABASE_HOST, password=DATABASE_PASSWORD)
    psql_cursor = psql_connection.cursor()
    psql_cursor.execute("INSERT INTO baza VALUES ({}, {}, \'{}\');".format(book_id, page_no, page_html_with_base64_imgs))
    psql_connection.commit(); psql_cursor.close(); psql_connection.close()

# telegram - /start command
def start_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Witaj, jestem odrabiamy-telegram!\nZerknij na /pomoc")

# telegram - /help command
def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Help and short instruction:\n\n/exercise \[URL\] \- bot will send specified exercise in a PNG image, URL must be in a format: "\
         + "```https://odrabiamy.pl/subject-name/book\-id/page\-number/exercise\-id```"\
         + "\n\n/page \[URL\] \- bot will send exercises in specified page in a PNG image, URL must be in a format: "\
         + "```https://odrabiamy.pl/subject-name/book\-id/page\-number```\n\(or either like in the /exercise command\)"
         , parse_mode='MarkdownV2')

# telegram - /pomoc command
def pomoc_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Pomoc i krótka instrukcja:\n\n/zadanie \[URL\] lub /exercise \[URL\] \- bot odeśle określone zadanie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer/zadanie\-id```"\
         + "\n\n/strona \[URL\] lub /page \[URL\] \- bot odeśle zadania zawarte w określonej stronie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer```\n\(lub tak jak w komendzie /zadanie\)"
         , parse_mode='MarkdownV2')

def get_page_or_exercise_cmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        global book_id, page_no, chosen_exercise_id, user, book_name
        user = update.message.from_user
        try:
            urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
            subject = urlArguments[1]
            book_id = urlArguments[2].split('-')[1]
            page_no = urlArguments[3].split('-')[1]
        except IndexError:
            update.message.reply_text('Niepoprawny adres URL\. Składnia musi wyglądać tak:\n```https://odrabiamy.pl/<nazwa_przedmiotu>/ksiazka-<id>/strona-<numer>```lub opcjonalnie na końcu z ```/zadanie-<id>```', parse_mode='MarkdownV2')
            print('User \"{}\" (id: {}) requested a bad link - nothing happens'.format(user['username'], user['id']))
            return
        print('User \"{}\" (id: {}) requested:'.format(user['username'], user['id']))
        try:
            chosen_exercise_id = urlArguments[4].split('-')[1]
        except IndexError:
            chosen_exercise_id = 'null'
        print(f'subject: {subject}\nbook_id: {book_id}\npage_no: {page_no}\nchosen_exercise_id: {chosen_exercise_id}')
        update.message.reply_text(f'Przedmiot: {subject}\nIdentyfikator książki: {book_id}\nStrona: {page_no}\nIdentyfikator zadania: {chosen_exercise_id}')

        get_book = requests.get(url=f'https://odrabiamy.pl/api/v3/books/{book_id}').content.decode('utf-8')
        if json.loads(get_book).get('name') == None:
            print('Wrong book_id\n')
            return
        else:
            book_name = str(json.loads(get_book).get('name'))

        psql_connection = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, host=DATABASE_HOST, password=DATABASE_PASSWORD)
        psql_cursor = psql_connection.cursor()
        psql_cursor.execute("SELECT content FROM baza\
                        WHERE book_id={} AND page_no={};".format(book_id, page_no))
        fetched_data = str(psql_cursor.fetchall())
        clean_data = fetched_data.lstrip('[(\'').rstrip('\',)]')
        psql_cursor.close(); psql_connection.close()
        if clean_data == "":
            print('Requesting download from server...\n')
            page_download()
            psql_connection = psycopg2.connect(dbname=DATABASE_NAME, user=DATABASE_USER, host=DATABASE_HOST, password=DATABASE_PASSWORD)
            psql_cursor = psql_connection.cursor()
            psql_cursor.execute("SELECT content FROM baza\
                            WHERE book_id={} AND page_no={};".format(book_id, page_no))
            fetched_data = str(psql_cursor.fetchall())
            clean_data = fetched_data.lstrip('[(\'').rstrip('\',)]')
            psql_cursor.close(); psql_connection.close()
            requestOrLocal = 'R'
        else:
            print('Opening from local...\n')
            requestOrLocal = 'L'

        soupFromFile = BeautifulSoup(clean_data, 'html.parser')
        if chosen_exercise_id != 'null':
            getFileContents = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\"Arial\",sans-serif;\">{book_name}</h1>' + str(soupFromFile.find('div', class_=f'exercise-{chosen_exercise_id}').extract())
        else:
            getFileContents = str(soupFromFile)
        
        soupFile = BeautifulSoup(getFileContents, 'html.parser')
        page_html_clean = str(soupFile).replace('\\xa0', ' ')

        print('Starting PNG Capture...')
        with sync_playwright() as browser_component:
            for browser_type in [browser_component.firefox]:
                browser = browser_type.launch()
                page = browser.new_page()
                page.set_content('{}'.format(page_html_clean))
                finalPngOutput = page.screenshot(full_page=True)
                browser.close()
        print('Completed PNG Capture')

        context.bot.send_document(update.effective_chat.id,
            BytesIO(finalPngOutput),filename=f"{requestOrLocal}_{book_name}_Strona_{page_no}.png")
        print('Sent!')

# telegram - handle commands and redirect to functions
updater.dispatcher.add_handler(CommandHandler('start', start_cmd))
updater.dispatcher.add_handler(CommandHandler('help', help_cmd))
updater.dispatcher.add_handler(CommandHandler('pomoc', pomoc_cmd))
updater.dispatcher.add_handler(CommandHandler('get', get_page_or_exercise_cmd))

# telegram - start bot
updater.start_polling()
print('\nBot started successfully!')

# To-Do: remove this and find a better alternative
page_html = ' '
page_html_with_base64_imgs = ' '