# urlArguments = input().split('odrabiamy.pl')[1].split(' ')[0].split('/')
# subject = urlArguments[1]        
# bookId = urlArguments[2].split('-')[1]
# pageNo = urlArguments[3].split('-')[1]
# try:
#     exerciseId = urlArguments[4].split('-')[1]
# except IndexError:
#     exerciseId = 'null'
# print("subject: " + subject + "\nbookId: " + bookId + "\npageNo: " + pageNo + "\nexerciseId: " + exerciseId)
import asyncio, requests, json, time, base64
from pyppeteer import launch
from bs4 import BeautifulSoup

async def generatePng():
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    newPage = await browser.newPage()
    pg = '<p><img alt="" height="397" src="https://prod.odrabiamy-assets.pl/uploads/content_image/image/74358/0yEjAVgqp6zLVivIbzjrCw%3D%3D_1f848d5f103151b2fd973cae2b2350032cf810354cf3826457df11e235ecb7eb.jpg" width="443"/> </p>        <p><img alt="" height="547" src="https://prod.odrabiamy-assets.pl/uploads/content_image/image/74359/4Wk1XFUHXl%2BIEFUZN%2BqpWQ%3D%3D_f741933aea625ff23f2c2ae13f49f80157f0f16310b968a5f45a5cd7dbbba207.jpg" width="497"/></p>        <p><img alt="" height="446" src="https://prod.odrabiamy-assets.pl/uploads/content_image/image/74360/0Rl%2BAz3XJd/75ibYKPcLwA%3D%3D_6399bd22108bf209e5f74595c84275b4c27998a3cccc46cab56129350534813d.jpg" width="444"/></p>        <p><img alt="" height="598" src="https://prod.odrabiamy-assets.pl/uploads/content_image/image/74361/2xrvkuquXQioIpbBnnrQxw%3D%3D_e401104107bca258fdc0defb19d87ed3ba96efdf62f83e4abfa448970eebe9a1.jpg" width="545"/></p>'
    soup = BeautifulSoup(pg, 'html.parser')
    img_num = 0
    for img in soup.find_all('img'):
        data = img['src']
        try:
            r = requests.get(data)
            rBytes = bytes(r.content, 'utf-8')
            encodeImg = str(base64.b64encode(rBytes))
            # encodeImg = base64.b64encode(r.content)
            print(str(encodeImg) + "\n\n\n\n\n")
            soup.find('img', src=data)['src'] = str(f'data:image/jpg;base64,{encodeImg}')
            # with open(f'exId-{img_num}.jpg','wb') as f:
            img_num += 1
            #     f.write(r.content)
            #     f.close()
        except:
            pass
    await newPage.goto('data:text/html;charset=utf-8,' + str(soup), {'waitUntil':'domcontentloaded'})
    # await newPage.goto('data:text/html;charset=utf-8,' + pg , {'waitUntil':'networkidle0'})
    time.sleep(1); global finalPngOutput
    finalPngOutput = await newPage.screenshot({'path':'saved.png', 'fullPage': 'true'})
    await browser.close()

runGeneratePng = asyncio.new_event_loop()
asyncio.set_event_loop(runGeneratePng)
print('Starting PNG Capture...')
runGeneratePng.run_until_complete(generatePng())
print('Completed PNG Capture')