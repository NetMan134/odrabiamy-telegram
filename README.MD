# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Usage
1. Required libraries can be downloaded via `pip install -r requirements`
2. Set `ODRABIAMY_LOGIN`, `ODRABIAMY_PASS` and `TELEGRAM_BOT_TOKEN` environment variables
3. Run the script! (`python odrabiamy-bot-telegram.py`)

## Limit
Odrabiamy.pl has a limit for browsing solutions to exercises, it's 60 exercises a day, and it resets at 12:00 AM every day.
Script after downloading about ~45 pages may crash, and on Odrabiamy.pl webpage, a warning message shown below will be visible.
If you want to continue with acquiring data via this bot, click "Got it" and continue.

(add a odrabiamy warning message here)

## Inspiration(s)
* doteq/odrabiamy-bot
* KartoniarzEssa/BetterOdrabiamyDownloader

## To-Do list:
- [ ] secure way of storing secrets
- [X] remove unused code (done for now)
- [ ] remove MORE unused code
- [ ] fix doubling of exercises when executing /strona multiple times
- [X] add a simple /help dialog with genuine help options (done for now)
- [ ] docker
- [ ] docker-compose

## License
This project is covered under GNU General Public License Version 3.