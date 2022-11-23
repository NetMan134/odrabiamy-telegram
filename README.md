# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Usage (python bare-metal) (postgresql docker compose)
<!-- 1. Setup a PostgreSQL server: -->
<!-- 1. Use PostgreSQL docker compose (linux)<br> -->
1. cd into postgresql-docker,
2. modify docker-compose.yml to satisfy your needs (remember the changes for later!):
    - change `POSTGRES_USER` to your choice,
    - change `POSTGRES_PASSWORD` to your choice,
    - change `POSTGRES_DB` to your choice,
    - change `5432:5432` to `<PORT>:5432`, where `<PORT>` is your choice (you can leave it as default).
3. run `docker-compose up -d` or `docker compose up -d` in that directory,
4. assuming the previous command completed without errors, acquire `psql` executable most likely from your package manager,
5. run `PGPASSWORD=<POSTGRES_PASSWORD> psql -h "localhost" -U "<POSTGRES_USER>" -d "<POSTGRES_DB>" -c 'CREATE TABLE IF NOT EXISTS <POSTGRES_TABLE> (book_id int not null, page_no int not null, exercises text not null, content text not null);'` and replace angle brackets with their values of your choice, (save your chosen `<POSTGRES_TABLE>` for later),
6. cd into main folder of the repository,
7. edit run.sh to satisfy your needs:
    - change `ODRABIAMY_LOGIN` to your odrabiamy account email,
    - change `ODRABIAMY_PASS` to your odrabiamy account password,
    - change `TG_TOKEN` to your Telegram token acquired from [BotFather](https://t.me/@BotFather "BotFather"),
    - leave `DB_ADDRESS` as `localhost`,
    - change `DB_USER` to your chosen change previously,
    - change `DB_PASS` to your chosen change previously,
    - change `DB_NAME` to your chosen change previously,
    - change `DB_TABLE` to your chosen change previosly,
    - change `DB_PORT` to your chosen change previosly.
8. run:
    - `python3 -m venv odrabiamy-venv`
    - `source odrabiamy-venv/bin/activate`
    - `pip install -r requirements.txt`
    - `playwright install`
    - `chmod a+x run.sh`
9. launch run.sh! (`./run.sh`)


    <!-- !["postgresql table config"](https://raw.githubusercontent.com/NetMan134/odrabiamy-telegram/master/postgresql-table.png "postgresql table config")<br> -->
<!-- 3. Set environment variables:
    * `ODRABIAMY_LOGIN`,
    * `ODRABIAMY_PASS`,
    * `TELEGRAM_BOT_TOKEN`,
    * `DB_ADDRESS`,
    * `DB_USER`,
    * `DB_PASS`,
    * `DB_NAME`
4. Run the script! (`python odrabiamy-bot-telegram.py`) -->
<!-- 
## Usage with docker-compose (not recommended FOR NOW, need to check this later)
1. Edit docker-compose.yml, set environment variables:
    * `ODRABIAMY_LOGIN`,
    * `ODRABIAMY_PASS`,
    * `TELEGRAM_BOT_TOKEN`,
    * `DB_ADDRESS`,
    * `DB_USER`,
    * `DB_PASS`,
    * `DB_NAME`
2. Run docker-compose `docker-compose up` (need to check this later) -->

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
- [ ] python - docker, docker-compose
- [ ] clean-up code
- [ ] secure way of storing secrets

## Warning
Using odrabiamy.pl API with external programs, scripts is possible only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is covered under GNU General Public License Version 3.