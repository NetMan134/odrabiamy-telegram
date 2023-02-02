# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Installation (bare-metal python, dockerized postgresql) 
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
    - `pip install python-telegram-bot[job-queue]` - warning, for this command better use bash. zsh for example can interpret the square brackets incorrectly and spit out an error 
    - `playwright install`
    - `chmod a+x run.sh`

## Launching and managemenmt
1. to start the bot, cd into the bot directory, run `source odrabiamy-venv/bin/activate` and then launch run.sh (`./run.sh`)
2. whitelist - if you try to interact with the bot, it will spit out a message about contacting the administrator (in polish for end-users friendliness) also providing user's ID - the user has to message you in order for you to acquire this ID (of course from users that you want to have access to your instance of this bot) - then insert it into `whitelist.txt` - you can do that on the fly, in other words you don't have to restart the bot every time you add a new user to the whitelist<br>Lines with # at the start qualify as comments, IDs should be put in their own line without any unwanted characters besides numbers of course (duh), spaces etc...<h3 style="margin:0;padding:0;">Example `whitelist.txt`:</h3>
    ```
    # A comment, for example who does this ID below belong to
    1234567890
    # John Smith
    9876543215
    # Max Deidre
    6565656566
    # [etc...]
    4323424324
    # idk a psychopath or sth
    9090678467
    ```

## Usage
People have 2 options to interact with the bot
1. /start - bot will ask for a link, and will show a button list of exercises from the chosen page and beside them 2 options: split and all. when the exercise number is chosen, bot will send only the specified exercise. when split will be chosen, bot will seperate all exercises from this page for every individual image. when all will be chosen, bot will send all exercises from this page in one image.
2. /get - the get syntax is: /get `<URL to odrabiamy>`, depending on if the link redirects to the whole page or a specific exercise, bot will send the whole page OR a specific exercise.

## Limit
Odrabiamy.pl has a limit for browsing solutions to exercises, it's 60 exercises a day, and it resets at 12:00 AM every day.
Script after downloading about ~45 pages may crash, and on Odrabiamy.pl webpage, a warning message shown below will be visible.<br>
!["odrabiamy.pl warning message"](https://raw.githubusercontent.com/NetMan134/odrabiamy-telegram/master/warning.png "odrabiamy.pl warning message")<br>
If you want to continue with acquiring data via this bot, click "Got it" and continue.

## Inspiration(s)
* [doteq/odrabiamy-bot](https://github.com/doteq/odrabiamy-bot "doteq/odrabiamy-bot")
* [m1chaelbarry/odrabiamy-bot](https://github.com/m1chaelbarry/odrabiamy-bot "m1chaelbarry/odrabiamy-bot")
* [KartoniarzEssa/BetterOdrabiamyDownloader](https://github.com/KartoniarzEssa/BetterOdrabiamyDownloader "KartoniarzEssa/BetterOdrabiamyDownloader")

## To-Do list:
- [X] use postgresql
- [ ] provide a user-friendly first-time run shell script
- [ ] full dockerization
- [ ] code clean-up
- [ ] more secure way of storing secrets

## Warning
Using odrabiamy.pl API with external programs, scripts is allowed only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is licensed under GNU General Public License Version 3.
See [LICENSE](https://github.com/NetMan134/odrabiamy-telegram/blob/master/LICENSE) for more information.
