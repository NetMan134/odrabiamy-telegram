# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Usage
1. Download required libraries via `pip install -r requirements`
2. Set `ODRABIAMY_LOGIN`, `ODRABIAMY_PASS` and `TELEGRAM_BOT_TOKEN` environment variables
3. Run the script! (`python odrabiamy-bot-telegram.py`)

## Usage with docker-compose
1. Edit docker-compose.yml - set `ODRABIAMY_LOGIN`, `ODRABIAMY_PASS` and `TELEGRAM_BOT_TOKEN` environment variables
2. Run docker-compose `docker-compose up` (does not work now, take a look at the todo list)

## Limit
Odrabiamy.pl has a limit for browsing solutions to exercises, it's 60 exercises a day, and it resets at 12:00 AM every day.
Script after downloading about ~45 pages may crash, and on Odrabiamy.pl webpage, a warning message shown below will be visible.<br>
!["odrabiamy.pl warning message"](https://raw.githubusercontent.com/NetMan134/odrabiamy-telegram/netman/warning.png "odrabiamy.pl warning message")<br>
If you want to continue with acquiring data via this bot, click "Got it" and continue.

## Inspiration(s)
* [doteq/odrabiamy-bot](https://github.com/doteq/odrabiamy-bot "doteq/odrabiamy-bot")
* [KartoniarzEssa/BetterOdrabiamyDownloader](https://github.com/KartoniarzEssa/BetterOdrabiamyDownloader "KartoniarzEssa/BetterOdrabiamyDownloader")

## To-Do list:
- [ ] secure way of storing secrets
- [X] remove unused code (done for now)
- [ ] clean the code MORE
- [X] fix doubling of exercises when executing /strona multiple times (done for now, do it better!)
- [X] add a simple /help dialog with genuine help options (done for now)
- [x] docker, docker-compose
- [ ] fix chromium pyppeteer on docker

## Warning
Using odrabiamy.pl API with external programs, scripts is possible only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is covered under GNU General Public License Version 3.