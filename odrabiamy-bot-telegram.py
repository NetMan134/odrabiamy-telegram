import requests, json, asyncio
from pyppeteer import launch
from io import BytesIO
from os import getenv
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler


# ODRABIAMY MANAGEMENT

login = getenv('ODRABIAMY_LOGIN')
pwd = getenv('ODRABIAMY_PASS')

updater = Updater(getenv('TELEGRAM_BOT_TOKEN'), use_context=True)


def get_token(user, password):
    try:
        rpost = requests.post(url=('https://odrabiamy.pl/api/v2/sessions'), json=({"login": f"{user}", "password": f"{password}"})).content
        token = json.loads(rpost).get('data').get('token')
        return token
    except:
        return False


token = get_token(login, pwd)

allofem = ' '

# ODRABIAMY DOWNLOAD
def down_page_whole():
    rget = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page}/{bookid}', headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {token}'}).content.decode('utf-8')
    lists = json.loads(rget).get('data')
    print('Wybierz zadanie: \n')
    for exercise in lists:
        print(exercise['id'])
        numbera = exercise['number']
        exe_id = str(exercise['id'])
        solutiona = exercise['solution']
        print(numbera)
        print(solutiona)
        book_name = exercise['book']['name']
        print(book_name)
        global allofem
        allofem += "<h1 style=\"font-weight:700;color:#200;\">" + book_name + "<br>Zadanie, id:" + exe_id + "<br>nr: " + numbera + "/" + page + "</h1><br>" + solutiona


def down_page():
    rget = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page}/{bookid}', headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {token}'}).content.decode('utf-8')
    lists = json.loads(rget).get('data')
    a = 0
    print('Wybierz zadanie: \n')
    for exercise in lists:
        print(a+1,": ")
        # print(lists[a]['number'])
        print(lists[a]['id'])
        print(exercise['id'])
        if exercise['id'] == exe_id_written:
            print('WPISANE ZADANIE W BOTA ZGADZA SIE')
            break
        else:
            print('NIE NIE NIE NIE WPISANE ZADANIE W BOTA NIEZGADZA SIE')
        a += 1
    print(exe_id_written)
    b = 0
    while b <= a:
        print(lists[b]['id'])
        if str(lists[b]['id']) == str(exe_id_written):
            numbera = lists[b]['number']
            exe_id = str(lists[b]['id'])
            solutiona = lists[b]['solution']
            print(numbera)
            print(solutiona)
            book_name = lists[b]['book']['name']
            print(book_name)
            global allofem
            allofem = "<h1 style=\"font-weight:700;color:#200;\">" + book_name + "<br>Zadanie, id:" + exe_id + "<br>nr: " + numbera + "/" + page + "</h1><br>" + solutiona
            break
        else:
            print('czekaj...')
        b += 1

# TELEGRAM BOT MANAGEMENT
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "seks!")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("Your Message")


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)
  
  
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def odrabiamy(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        urlArgs = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookid, page, exe_id_written, usera
        bookid = urlArgs[2].split('-')[1]
        page = urlArgs[3].split('-')[1]
        exe_id_written = urlArgs[4].split('-')[1]
        update.message.reply_text("bookId:" + bookid + ", page: " + page + ", exerciseId: " + exe_id_written)
        usera = update.message.from_user
        down_page()
        print('checkpoint\n')
        update.message.reply_text("downloaded successfully, generating image...")
        # print(allofem)

        async def mainofpng():
            browsera = await launch(
                handleSIGINT=False,
                handleSIGTERM=False,
                handleSIGHUP=False
            )
            pagech = await browsera.newPage()
            await pagech.goto("data:text/html;charset=utf-8," + allofem, {'waitUntil':'networkidle0'})
            global screenshot_of_exercise
            screenshot_of_exercise = await pagech.screenshot({'fullPage': 'true'})
            await browsera.close()

        loopng = asyncio.new_event_loop()
        asyncio.set_event_loop(loopng)
        print('chk1')
        loopng.run_until_complete(mainofpng())
        print('chk2')
        context.bot.send_document(update.effective_chat.id, BytesIO(screenshot_of_exercise),filename=f"sonic_porno.png")


def odrabiamypage(update: Update, context: CallbackContext):
    if 'odrabiamy.pl' in update.message.text:
        urlArgs = update.message.text.split('odrabiamy.pl')[1].split(' ')[0].split('/')
        global bookid, page, usera
        bookid = urlArgs[2].split('-')[1]
        page = urlArgs[3].split('-')[1]
        update.message.reply_text("bookId:" + bookid + ", page: " + page)
        usera = update.message.from_user

        down_page_whole()
        print('checkpoint')
        update.message.reply_text("downloaded page successfully, generating image...")
        # print(allofem)

        async def mainofpng():
            browsera = await launch(
                handleSIGINT=False,
                handleSIGTERM=False,
                handleSIGHUP=False
            )
            pagech = await browsera.newPage()
            await pagech.goto("data:text/html;charset=utf-8," + allofem, {'waitUntil':'networkidle0'})
            global screenshot_of_exercise
            screenshot_of_exercise = await pagech.screenshot({'path': 'dzialacXD.png', 'fullPage': 'true'})
            # screenshot_of_exercise = await pagech.screenshot({'fullPage': 'true'})
            await browsera.close()

        # asyncio.get_event_loop().run_until_complete(mainofpng())
        loopng = asyncio.new_event_loop()
        asyncio.set_event_loop(loopng)
        print('chk1')
        loopng.run_until_complete(mainofpng())
        print('chk2')
        context.bot.send_document(update.effective_chat.id, BytesIO(screenshot_of_exercise),filename=f"sonic_porno_big.png")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('zadanie', odrabiamy))
updater.dispatcher.add_handler(CommandHandler('strona', odrabiamypage))

updater.start_polling()
