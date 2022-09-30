import requests, json, asyncio
from pyppeteer import launch
from io import BytesIO
from os import getenv
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler


# odrabiamy - login variables (stored in environment)
odrabiamyLogin = getenv('ODRABIAMY_LOGIN')
odrabiamyPass  = getenv('ODRABIAMY_PASS')

# telegram - bot token variables (stored in environment variable)
updater = Updater(
    getenv('TELEGRAM_BOT_TOKEN'),
use_context=True)

# odrabiamy - get token
def getOdrabiamyToken(email, password):
    try:
        requestTokenPost = requests.post(url='https://odrabiamy.pl/api/v2/sessions',
            json=({"login": f"{email}", "password": f"{password}"})).content
        odrabiamyToken = json.loads(requestTokenPost).get('data').get('token')
        return odrabiamyToken
    except:
        return False

# odrabiamy - assign token and check login details or premium subscription
odrabiamyToken = getOdrabiamyToken(odrabiamyLogin, odrabiamyPass)
if odrabiamyToken == False:
    print('Incorrect login details for odrabiamy.\nOr perhaps you don\'t have premium?')
    quit()


# odrabiamy - download page exercise
def downloadPageExercise():
    requestPageGet = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{pageNo}/{bookId}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {odrabiamyToken}'}).content.decode('utf-8')
    listOfData = json.loads(requestPageGet).get('data')
    forExercise = forExercises = 0
    for exercise in listOfData:
        global bookName, exerciseNo, fullHtml
        if exercise['id'] == exerciseId:
            break
        forExercise += 1
    while forExercises <= forExercise:
        if str(listOfData[forExercises]['id']) == str(exerciseId):
            bookName = listOfData[forExercises]['book']['name']
            exerciseNo = listOfData[forExercises]['number']
            solution = listOfData[forExercises]['solution']
            fullHtml = "<h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">"\
             + bookName + "<br>Zadanie " + exerciseNo + ", Strona " + pageNo + "</h1><br>" + solution
            break
        forExercises += 1

# odrabiamy - download page
def downloadPage():
    requestPageGet = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{pageNo}/{bookId}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {odrabiamyToken}'}).content.decode('utf-8')
    listOfData = json.loads(requestPageGet).get('data')
    global bookName, exerciseNo, fullHtml
    fullHtml = ' ' # odrabiamy - downloaded html (temporary - TO-DO: do it better and remove this)
    for exercise in listOfData:
        bookName = exercise['book']['name']
        exerciseNo = exercise['number']
        solution = exercise['solution']
        fullHtml += "<h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">"\
            + bookName + "<br>Zadanie " + exerciseNo + ", Strona " + pageNo + "</h1><br>" + solution


# telegram - /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Witaj, jestem odrabiamy-telegram!\nZerknij na /pomoc lub /help ")

# telegram - /help or /pomoc command
def help(update: Update, context: CallbackContext):
    update.message.reply_text("Pomoc i krótka instrukcja:\n\n/zadanie [URL] lub /exercise [URL] \- bot odeśle określone zadanie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer/zadanie\-id```"\
         + "\n\n/strona [URL] lub /page [URL] \- bot odeśle zadania zawarte w określonej stronie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer```\nlub tak jak w komendzie /zadanie"
         , parse_mode='MarkdownV2')

# telegram - /exercise or /zadanie command
def pageExerciseCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookId, pageNo, exerciseId, user
        subject = urlArguments[1]
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        exerciseId = urlArguments[4].split('-')[1]
        user = update.message.from_user
        print('User \"{}\" (id: {}) requested exercise download of:'.format(user['username'], user['id']))
        print("subject: " + subject + "\nbookId: " + bookId + "\npageNo: " + pageNo + "\nexerciseId: " + exerciseId)
        update.message.reply_text("Przedmiot: " + subject + "\nIdentyfikator książki: " + bookId + "\nStrona: " + pageNo + "\nIdentyfikator zadania: " + exerciseId)
        downloadPageExercise(); update.message.reply_text("Pobrano zadanie pomyślnie, generowanie zdjęcia...")

        async def generatePng():
            browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
            newPage = await browser.newPage(); await newPage.goto("data:text/html;charset=utf-8," + fullHtml, {'waitUntil':'networkidle0'})
            global finalPngOutput
            finalPngOutput = await newPage.screenshot({'fullPage': 'true'})
            await browser.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        context.bot.send_document(update.effective_chat.id,
            BytesIO(finalPngOutput),filename=f"{bookName}_Strona {pageNo}_Zadanie {exerciseNo}.png")
        print('Sent!\n')


# telegram - /page or /strona command
def pageCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        global bookId, pageNo, exerciseId, user
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        subject = urlArguments[1]        
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        user = update.message.from_user
        print('User \"{}\" (id: {}) requested page download of:'.format(user['username'], user['id']))
        print("subject: " + subject + "\nbookId: " + bookId + "\npageNo: " + pageNo)
        update.message.reply_text("Przedmiot: " + subject + "\nIdentyfikator książki: " + bookId + "\nStrona: " + pageNo)
        downloadPage(); update.message.reply_text("Pobrano stronę pomyślnie, generowanie zdjęcia...")

        async def generatePng():
            browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
            newPage = await browser.newPage(); await newPage.goto("data:text/html;charset=utf-8," + fullHtml, {'waitUntil':'networkidle0'})
            global finalPngOutput
            finalPngOutput = await newPage.screenshot({'fullPage': 'true'})
            await browser.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        context.bot.send_document(update.effective_chat.id,
            BytesIO(finalPngOutput),filename=f"{bookName}_Strona {pageNo}_Zadanie {exerciseNo}.png")


# telegram - handle commands and redirect to functions
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('pomoc', help))
updater.dispatcher.add_handler(CommandHandler('exercise', pageExerciseCmd))
updater.dispatcher.add_handler(CommandHandler('zadanie', pageExerciseCmd))
updater.dispatcher.add_handler(CommandHandler('page', pageCmd))
updater.dispatcher.add_handler(CommandHandler('strona', pageCmd))

# telegram - start bot
updater.start_polling()
print('Bot started successfully')

# odrabiamy - downloaded html (temporary - TO-DO: do it better and remove this)
fullHtml = ' '