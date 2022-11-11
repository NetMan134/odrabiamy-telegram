# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Usage
1. Download required dependencies via `pip install -r requirements.txt`
2. Setup a PostgreSQL server with a read-write UTF-8 encoded database with a "baza" table:
    !["postgresql table config"](https://raw.githubusercontent.com/NetMan134/odrabiamy-telegram/master/postgresql-table.png "postgresql table config")<br>
3. Set environment variables:
    * `ODRABIAMY_LOGIN`,
    * `ODRABIAMY_PASS`,
    * `TELEGRAM_BOT_TOKEN`,
    * `DB_ADDRESS`,
    * `DB_USER`,
    * `DB_PASS`,
    * `DB_NAME`
4. Run the script! (`python odrabiamy-bot-telegram.py`)

## Usage with docker-compose (not recommended FOR NOW, need to check this later)
1. Edit docker-compose.yml, set environment variables:
    * `ODRABIAMY_LOGIN`,
    * `ODRABIAMY_PASS`,
    * `TELEGRAM_BOT_TOKEN`,
    * `DB_ADDRESS`,
    * `DB_USER`,
    * `DB_PASS`,
    * `DB_NAME`
2. Run docker-compose `docker-compose up` (need to check this later)

## Limit
Odrabiamy.pl has a limit for browsing solutions to exercises, it's 60 exercises a day, and it resets at 12:00 AM every day.
Script after downloading about ~45 pages may crash, and on Odrabiamy.pl webpage, a warning message shown below will be visible.<br>
!["odrabiamy.pl warning message"](https://raw.githubusercontent.com/NetMan134/odrabiamy-telegram/master/warning.png "odrabiamy.pl warning message")<br>
If you want to continue with acquiring data via this bot, click "Got it" and continue.

## Inspiration(s)
* [doteq/odrabiamy-bot](https://github.com/doteq/odrabiamy-bot "doteq/odrabiamy-bot")
* [KartoniarzEssa/BetterOdrabiamyDownloader](https://github.com/KartoniarzEssa/BetterOdrabiamyDownloader "KartoniarzEssa/BetterOdrabiamyDownloader")

## To-Do list:
- [X] use postgresql
- [x] docker, docker-compose
- [ ] clean-up code
- [ ] secure way of storing secrets
- [ ] polish the /help dialog
- [ ] check if it works on docker (ex. playwright)

## Warning
Using odrabiamy.pl API with external programs, scripts is possible only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is covered under GNU General Public License Version 3.