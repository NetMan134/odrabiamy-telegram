import requests, json, asyncio
from pyppeteer import launch
from io import BytesIO
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


#ODRABIAMY MANAGEMENT


login = 'LOGIN DO ODRABIAMY'
pwd = 'HASLO DO ODRABIAMY'


def get_token(user, password):
    try:
        rpost = requests.post(url=('https://odrabiamy.pl/api/v2/sessions'), json=({"login": f"{user}", "password": f"{password}"})).content
        token = json.loads(rpost).get('data').get('token')
        return token
    except:
        return False

token = get_token(login, pwd)
# token = get_token(login, pwd)
# bookid = input('daj id ksiazki: ')
# page = input('daj strone: ')

allofem = ' '
exercisea = ' '

#pyppeter PNG GENERATOR
async def mainofpng():
    browsera = await launch()
    pagech = await browsera.newPage()
    await pagech.goto("data:text/html;charset=utf-8," + allofem, {'waitUntil':'networkidle0'})
    global screenshot_of_exercise
    screenshot_of_exercise = await pagech.screenshot({'path': 'dziala.png', 'fullPage': 'true'})
    await browsera.close()

#ODRABIAMY DOWNLOAD
def down_page():
    rget = requests.get(url=f'https://odrabiamy.pl/api/v2/exercises/page/premium/{page}/{bookid}', headers={'user-agent':'new_user_agent-huawei-144','Authorization': f'Bearer {token}'}).content.decode('utf-8')
    lists = json.loads(rget).get('data')
    a = 0
    print('Wybierz zadanie: \n')
    for exercise in lists:
        print(a+1,": ")
        print(lists[a]['number'])
        print(exercise['number'])
        if exercise['number'] == exercisea:
            print('WPISANE ZADANIE W BOTA ZGADZA SIE')
            # a += 1
            break
        else:
            print('NIE NIE NIE NIE WPISANE ZADANIE W BOTA NIEZGADZA SIE')
        a += 1
    print(exercisea)
    b = 0
    while b <= a:
        if lists[b]['number'] == exercisea:
            numbera = lists[b]['number']
            solutiona = lists[b]['solution']
            print(numbera)
            print(solutiona)
            book_name = lists[b]['book']['name']
            print(book_name)
            global allofem
            allofem = "<h1 style=\"font-weight:700;color:#200;\">" + book_name + "<br>Zadanie " + numbera + "/" + page + "</h1><br>" + solutiona
        else:
            print('czekaj...')
        b += 1


#TELEGRAM BOT MANAGEMENT
updater = Updater("TOKEN HTTP DO BOTA TELEGRAM",
                  use_context=True)

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
        urlArgsa = update.message.text.split('odrabiamy.pl')[1].split(' ')[1]
        global bookid, page, exercisea
        bookid = urlArgs[2].split('-')[1]
        page = urlArgs[3].split('-')[1]
        exercisea = urlArgsa
        update.message.reply_text(bookid + " " + page + " " + exercisea)
        down_page()
        print('checkpoint\n')
        update.message.reply_text("checkpoint\n\n1")
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
        context.bot.send_document(update.effective_chat.id, BytesIO(screenshot_of_exercise),filename=f"sexdziala.png")


def odczytajTest(update: Update, context: CallbackContext):
    token = get_token(login, pwd)
    update.message.reply_text('czekaj...' + token)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('odrabiamy', odczytajTest))
updater.dispatcher.add_handler(MessageHandler(Filters.text, odrabiamy))
updater.dispatcher.add_handler(MessageHandler(
    # Filters out unknown commands
    Filters.command, unknown))
  
# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
updater.start_polling()