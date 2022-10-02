import requests, json, asyncio, inspect, os.path, time
from pyppeteer import launch
from io import BytesIO
from os import getenv
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from bs4 import BeautifulSoup


# odrabiamy - login variables (stored in environment)
odrabiamyLogin = getenv('ODRABIAMY_LOGIN')
odrabiamyPass  = getenv('ODRABIAMY_PASS')

# telegram - bot token variables (stored in environment variable)
updater = Updater(
    getenv('TELEGRAM_BOT_TOKEN'),
use_context=True)

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

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
    global bookName, exerciseNo, fullHtml, writeHtmlToFile
        
    forExercise = forExercises = 0
    jsonExercisesDict = {}
    for exercise in listOfData:
        jsonExercisesDict[exercise['id']] = exercise['number']
        forExercise += 1
    bookName = listOfData[forExercises]['book']['name']
    # fullHtml = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">{bookName}</h1><br>'
    writeHtmlToFile = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">{bookName}</h1><br>'
    while forExercises < forExercise:
        exerciseNo = listOfData[forExercises]['number']
        solution = listOfData[forExercises]['solution']
        solutionParser = BeautifulSoup(solution, 'html.parser')

        for svgSmallObject in solutionParser.find_all('object', class_='small', type='image/svg+xml'):
            svgSmallObject.extract()

        for svgMathSmallObject in solutionParser.find_all('object', class_='math small', type='image/svg+xml'):
            svgMathSmallObject.extract()

        if not os.path.exists(f'{path}/{bookName}-{bookId}/{pageNo}'):
            os.makedirs(f'{path}/{bookName}-{bookId}/{pageNo}')
        
        writeHtmlToFile += f'<div id="exercise-"><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">Zadanie {exerciseNo}, Strona {pageNo}</h1>{solutionParser}<br>'

        forExercises += 1
    jsonExercisesObject = json.dumps(jsonExercisesDict, indent=forExercise)
    # jsonExercisesFile = open(f'{path}/{bookName}-{bookId}/{pageNo}/exercises.json', 'a+', encoding='utf-8')
    with open(f'{path}/{bookName}-{bookId}/{pageNo}/exercises.json', 'a+') as jsonExercisesFileOut:
        jsonExercisesFileOut.write(jsonExercisesObject)

    fileInside = open(f'{path}/{bookName}-{bookId}/{pageNo}/index.html', 'a+', encoding='utf-8')
    fileInside.write(writeHtmlToFile)
    fileInside.close()
    global requestLocal
    requestLocal = 'Request'

# def getPageFromDisk():
    

# telegram - /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Witaj, jestem odrabiamy-telegram!\nZerknij na /pomoc lub /help ")

# telegram - /help command
def help(update: Update, context: CallbackContext):
    update.message.reply_text("Help and short instruction:\n\n/exercise \[URL\] \- bot will send specified exercise in a PNG image, URL must be in a format: "\
         + "```https://odrabiamy.pl/subject-name/book\-id/page\-number/exercise\-id```"\
         + "\n\n/page \[URL\] \- bot will send exercises in specified page in a PNG image, URL must be in a format: "\
         + "```https://odrabiamy.pl/subject-name/book\-id/page\-number```\n\(or either like in the /exercise command\)"
         , parse_mode='MarkdownV2')

# telegram - /pomoc command
def pomoc(update: Update, context: CallbackContext):
    update.message.reply_text("Pomoc i krótka instrukcja:\n\n/zadanie \[URL\] lub /exercise \[URL\] \- bot odeśle określone zadanie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer/zadanie\-id```"\
         + "\n\n/strona \[URL\] lub /page \[URL\] \- bot odeśle zadania zawarte w określonej stronie w pliku PNG, URL musi być w formacie: "\
         + "```https://odrabiamy.pl/nazwa\-przedmiotu/ksiazka\-id/strona\-numer```\n\(lub tak jak w komendzie /zadanie\)"
         , parse_mode='MarkdownV2')

# telegram - /exercise or /zadanie command
def pageExerciseCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookId, pageNo, exerciseId, user
        user = update.message.from_user
        print('User \"{}\" (id: {}) requested exercise download of:'.format(user['username'], user['id']))
        subject = urlArguments[1]
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        exerciseId = urlArguments[4].split('-')[1]
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
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookId, pageNo, exerciseId, user
        user = update.message.from_user
        print('User \"{}\" (id: {}) requested page download of:'.format(user['username'], user['id']))
        subject = urlArguments[1]        
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        print(f'subject: {subject}\nbookId: {bookId}\npageNo: {pageNo}')
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


def pageDiskCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        global bookId, pageNo, exerciseId, user, requestLocal, bookName
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        subject = urlArguments[1]        
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        user = update.message.from_user
        print('User \"{}\" (id: {}) requested page OPEN of:'.format(user['username'], user['id']))
        print("subject: " + subject + "\nbookId: " + bookId + "\npageNo: " + pageNo)
        update.message.reply_text("Przedmiot: " + subject + "\nIdentyfikator książki: " + bookId + "\nStrona: " + pageNo)
        # downloadPage(); update.message.reply_text("Pobrano stronę pomyślnie, generowanie zdjęcia...")
        bookGetRequest = requests.get(url=f'https://odrabiamy.pl/api/v3/books/{bookId}').content.decode('utf-8')
        listBook = json.loads(bookGetRequest)
        if listBook.get('name') == None:
            print('Wrong bookId\n')
            return
        
        bookName = listBook['name']
        if not os.path.exists(f'{path}/{bookName}-{bookId}/{pageNo}'):
            print('Requesting download from server...\n')
            downloadPage()
        else:
            print('Opening from local...\n')
            requestLocal = 'Local'
        
        global openFile
        openFile = open(f'{path}/{bookName}-{bookId}/{pageNo}/index.html', 'r', encoding='utf-8').read()

        async def generatePng():
            browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
            newPage = await browser.newPage(); await newPage.goto("data:text/html;charset=utf-8," + openFile, {'waitUntil':'networkidle0'})
            time.sleep(0.5)
            global finalPngOutput
            finalPngOutput = await newPage.screenshot({'fullPage': 'true'})
            time.sleep(0.5)
            await browser.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        context.bot.send_document(update.effective_chat.id,
            BytesIO(finalPngOutput),filename=f"{requestLocal}_{bookName}_Strona_{pageNo}.png")


# telegram - handle commands and redirect to functions
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('pomoc', pomoc))
updater.dispatcher.add_handler(CommandHandler('exercise', pageExerciseCmd))
updater.dispatcher.add_handler(CommandHandler('zadanie', pageExerciseCmd))
updater.dispatcher.add_handler(CommandHandler('dysk', pageDiskCmd))
updater.dispatcher.add_handler(CommandHandler('disk', pageDiskCmd))
updater.dispatcher.add_handler(CommandHandler('page', pageCmd))
updater.dispatcher.add_handler(CommandHandler('strona', pageCmd))

# telegram - start bot
updater.start_polling()
print('\nBot started successfully')

# odrabiamy - downloaded html (temporary - TO-DO: do it better and remove this)
fullHtml = ' '
writeHtmlToFile = ' '