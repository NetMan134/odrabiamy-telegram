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
    print('\nIncorrect login details for odrabiamy.\nOr perhaps you don\'t have premium?\n(Or no internet connection?)')
    quit()
print(odrabiamyToken)
# odrabiamy - download page
def downloadPage():
    requestPageGet = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{pageNo}/{bookId}',
        headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {odrabiamyToken}'}).content.decode('utf-8')
    jsonData = json.loads(requestPageGet).get('data')
    global bookName, jsonExerciseNo, writeHtmlToFile
    forExercise = forExercises = 0
    for exercise in jsonData:
        forExercise += 1
    # bookName = jsonData[forExercises]['book']['name']
    writeHtmlToFile = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">{bookName}</h1>'
    while forExercises < forExercise:
        jsonExerciseNo = jsonData[forExercises]['number']
        jsonExerciseId = jsonData[forExercises]['id']
        gottenSolution = jsonData[forExercises]['solution']
        parsedSolution = BeautifulSoup(gottenSolution, 'html.parser')
        for svgSmallObject in parsedSolution.find_all('object', class_='small', type='image/svg+xml'):
            svgSmallObject.extract()
        for svgMathSmallObject in parsedSolution.find_all('object', class_='math small', type='image/svg+xml'):
            svgMathSmallObject.extract()
        if not os.path.exists(f'{path}/{bookName}-{bookId}/{pageNo}'):
            os.makedirs(f'{path}/{bookName}-{bookId}/{pageNo}')
        
        writeHtmlToFile += f'<div class="exercise-{jsonExerciseId}"><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">Zadanie {jsonExerciseNo}, Strona {pageNo}</h1>{parsedSolution}</div><br>'
        forExercises += 1
    
    fileInside = open(f'{path}/{bookName}-{bookId}/{pageNo}/index.html', 'a+', encoding='utf-8')
    fileInside.write(writeHtmlToFile)
    fileInside.close()

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

def processCmd(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        global bookId, pageNo, exerciseId, user, bookName

        user = update.message.from_user
        print('User \"{}\" (id: {}) requested:'.format(user['username'], user['id']))
        
        urlArguments = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        subject = urlArguments[1]
        bookId = urlArguments[2].split('-')[1]
        pageNo = urlArguments[3].split('-')[1]
        try:
            exerciseId = urlArguments[4].split('-')[1]
        except IndexError:
            exerciseId = 'null'
        print(f'subject: {subject}\nbookId: {bookId}\npageNo: {pageNo}\nexerciseId: {exerciseId}')
        update.message.reply_text(f'Przedmiot: {subject}\nIdentyfikator książki: {bookId}\nStrona: {pageNo}\nIdentyfikator zadania: {exerciseId}')

        bookGetRequest = requests.get(url=f'https://odrabiamy.pl/api/v3/books/{bookId}').content.decode('utf-8')
        if json.loads(bookGetRequest).get('name') == None:
            print('Wrong bookId\n')
            return
        else:
            bookName = str(json.loads(bookGetRequest).get('name'))

        if not os.path.exists(f'{path}/{bookName}-{bookId}/{pageNo}'):
            print('Requesting download from server...\n')
            downloadPage()
            requestOrLocal = 'R'
        else:
            print('Opening from local...\n')
            requestOrLocal = 'L'
        
        openFile = open(f'{path}/{bookName}-{bookId}/{pageNo}/index.html', 'r', encoding='utf-8').read()

        soupFromFile = BeautifulSoup(openFile, 'html.parser')
        if exerciseId != 'null':
            getFileContents = f'<head><meta charset="UTF-8"></head><h1 style=\"font-weight:700;color:#200;font-family:\'Arial\',sans-serif;\">{bookName}</h1>' + str(soupFromFile.find('div', class_=f'exercise-{exerciseId}').extract())
        else:
            getFileContents = str(soupFromFile)

        async def generatePng():
            browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False, args=['--allow-file-access-from-files', '--enable-local-file-accesses', '--no-sandbox'])
            newPage = await browser.newPage()
            soupFile = BeautifulSoup(getFileContents, 'html.parser')
            img_num = 0
            if not os.path.exists(f'/images/{pageNo}/{exerciseId}'):
                os.makedirs(f'/images/{pageNo}/{exerciseId}')

            for img in soupFile.find_all('img'):
                data = img['src']
                r = requests.get(data)
                soupFile.find('img', src=data)['src'] = str(f'http://127.0.0.1:8012/{pageNo}/{exerciseId}/{img_num}.jpg')
                with open(f'/images/{exerciseId}/{img_num}.jpg','wb') as f:
                    img_num += 1
                    f.write(r.content)
                    f.close()
            # await newPage.goto("data:text/html;charset=utf-8," + getFileContents, {'waitUntil':'networkidle0'})
            await newPage.goto("data:text/html;charset=utf-8," + str(soupFile), {'waitUntil':'networkidle0'})
            # await newPage.goto("data:text/html;charset=utf-8," + getFileContents, {'waitUntil':'domcontentloaded'})
            time.sleep(1); global finalPngOutput
            finalPngOutput = await newPage.screenshot({'fullPage': 'true'})
            await browser.close()

        runGeneratePng = asyncio.new_event_loop()
        asyncio.set_event_loop(runGeneratePng)
        print('Starting PNG Capture...')
        runGeneratePng.run_until_complete(generatePng())
        print('Completed PNG Capture')
        context.bot.send_document(update.effective_chat.id,
            BytesIO(finalPngOutput),filename=f"{requestOrLocal}_{bookName}_Strona_{pageNo}.png")

# telegram - handle commands and redirect to functions
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('pomoc', pomoc))
updater.dispatcher.add_handler(CommandHandler('get', processCmd))

# telegram - start bot
updater.start_polling()
print('\nBot started successfully')

# odrabiamy - downloaded html (temporary - TO-DO: do it better and remove this)
writeHtmlToFile = ' '