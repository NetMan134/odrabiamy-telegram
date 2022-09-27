import requests, json, asyncio
from pyppeteer import launch
from io import BytesIO
from os import getenv
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler


# ODRABIAMY MANAGEMENT

odrabiamyLogin = getenv('ODRABIAMY_LOGIN')
odrabiamyPass  = getenv('ODRABIAMY_PASS')

updater = Updater(
    getenv('TELEGRAM_BOT_TOKEN'),
use_context=True)

def getOdrabiamyToken(email, password):
    try:
        requestTokenPost = requests.post(url='https://odrabiamy.pl/api/v2/sessions', json=
        ({"login": f"{email}", "password": f"{password}"})).content
        token = json.loads(requestTokenPost).get('data').get('token')
        return token
    except:
        return False

token = getOdrabiamyToken(odrabiamyLogin, odrabiamyPass)
if token == False:
    print('Incorrect login details for odrabiamy.\nOr perhaps you don\'t have premium?')
    quit()

# ODRABIAMY DOWNLOAD
def downloadPage():
    requestPageGet = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page}/{bookid}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {token}'}).content.decode('utf-8')
    listOfData = json.loads(requestPageGet).get('data')
    for exercise in listOfData:
        global number, exe_id, solution, book_name, fullHtml
        number = exercise['number']
        exe_id = str(exercise['id'])
        solution = exercise['solution']
        book_name = exercise['book']['name']
        fullHtml += "<h1 style=\"font-weight:700;color:#200;\">" + book_name + "<br>Zadanie, id:"\
         + exe_id + "<br>nr: " + number + "/" + page + "</h1><br>" + solution


def downloadPageExercise():
    requestPageGet = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page}/{bookid}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {token}'}).content.decode('utf-8')
    listOfData = json.loads(requestPageGet).get('data')
    forExercise = forExercises = 0
    for exercise in listOfData:
        global number, exe_id, solution, book_name, fullHtml
        if exercise['id'] == exe_id_written:
            break
        forExercise += 1
    while forExercises <= forExercise:
        if str(listOfData[forExercises]['id']) == str(exe_id_written):
            number = listOfData[forExercises]['number']
            exe_id = str(listOfData[forExercises]['id'])
            solution = listOfData[forExercises]['solution']
            book_name = listOfData[forExercises]['book']['name']
            global fullHtml
            fullHtml = "<h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">"\
             + book_name + "<br>Zadanie " + number + ", Strona " + page + "</h1><br>" + solution
            break
        forExercises += 1

# TELEGRAM BOT MANAGEMENT
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Witaj, jestem odrabiamy-telegram!\nZerknij na /pomoc lub /help ")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("Pomoc i krótka instrukcja:\n\n/zadanie [URL] \- bot odeśle określone zadanie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer/zadanie\-id```"\
         + "\n\n/strona [URL] \- bot odeśle zadania zawarte w określonej stronie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer```\nlub tak jak w komendzie /zadanie"
         , parse_mode='MarkdownV2')

def pageExerciseCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        urlArgs = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookid, page, exe_id_written, usera
        usera = update.message.from_user
        bookid = urlArgs[2].split('-')[1]
        page = urlArgs[3].split('-')[1]
        exe_id_written = urlArgs[4].split('-')[1]
        print('User \"{}\" (id: {}) requested exercise download of:'.format(usera['username'], usera['id']))
        print("bookid: " + bookid + "\npage: " + page)
        update.message.reply_text("Identyfikator książki: " + bookid + "\nStrona: " + page + "\nIdentyfikator zadania: " + exe_id_written)
        downloadPageExercise()
        update.message.reply_text("downloaded successfully, generating image...")

        async def generatePng():
            browsera = await launch(
                handleSIGINT=False,
                handleSIGTERM=False,
                handleSIGHUP=False
            )
            pagech = await browsera.newPage()
            await pagech.goto("data:text/html;charset=utf-8," + fullHtml, {'waitUntil':'networkidle0'})
            global screenshot_of_exercise
            screenshot_of_exercise = await pagech.screenshot({'fullPage': 'true'})
            await browsera.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        context.bot.send_document(update.effective_chat.id,
        BytesIO(screenshot_of_exercise),filename=f"{book_name}_Strona {page}_Zadanie {number}.png")


def pageCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        global bookid, page, usera
        usera = update.message.from_user
        urlArgs = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        bookid = urlArgs[2].split('-')[1]
        page = urlArgs[3].split('-')[1]
        print('User \"{}\" (id: {}) requested page download of:'.format(usera['username'], usera['id']))
        print("bookid: " + bookid + "\npage: " + page)
        update.message.reply_text("Identyfikator książki: " + bookid + "\nStrona: " + page)

        downloadPage()
        update.message.reply_text("Pobrano stronę pomyślnie, generowanie zdjęcia...")

        async def generatePng():
            browsera = await launch(
                handleSIGINT=False,
                handleSIGTERM=False,
                handleSIGHUP=False
            )
            pagech = await browsera.newPage()
            await pagech.goto("data:text/html;charset=utf-8," + fullHtml, {'waitUntil':'networkidle0'})
            global screenshot_of_exercise
            screenshot_of_exercise = await pagech.screenshot({'fullPage': 'true'})
            await browsera.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        # context.bot.send_document(update.effective_chat.id, BytesIO(screenshot_of_exercise),filename=f"sonic_porno_big.png")
        context.bot.send_document(update.effective_chat.id, BytesIO(screenshot_of_exercise),filename=f"{book_name}_Strona {page}.png")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('pomoc', help))
updater.dispatcher.add_handler(CommandHandler('zadanie', pageExerciseCmd))
updater.dispatcher.add_handler(CommandHandler('strona', pageCmd))

updater.start_polling()
print('Bot started successfully')
fullHtml = ' '