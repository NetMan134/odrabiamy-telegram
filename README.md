# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for Odrabiamy.pl

# Update
The token can't seem to be retrieved anymore, so this projects is on hold...

## Installation (fully dockerized)
1. Clone this repository (`git clone https://github.com/NetMan134/odrabiamy-telegram`).
2. Make sure you have docker and docker compose plugin installed on your system.
3. Modify variables.env to your values:
    - `ODRABIAMY_LOGIN` Odrabiamy.pl email address,
    - `ODRABIAMY_PASS` Odrabiamy.pl password, 
    - `TG_TOKEN` Telegram bot token,
    - better leave PostgreSQL values as default unless you know what you're doing.
5. Run `docker compose up -d` in that directory.

### Updates
1. Stop the instance by running `docker compose down`.
2. Run `git pull` to acquire new commits.
3. Run `docker compose up -d --build`.

### Troubleshooting
If the containers behave weirdly, try rebuilding them.<br>
To do that, run: `docker compose down` and `docker compose up -d --build`.

## Installation (bare-metal) 
1. Make sure you have Python 3 installed on your system (for best compatibility, use 3.11.1).
2. Set up a PostgreSQL server with a database and ability to read/write, etc. (you can create a docker container with a postgres image), and run a sql instruction from `table.sql` file.
3. Modify `./run.sh` to your values:
    - `ODRABIAMY_LOGIN` Odrabiamy.pl email address,
    - `ODRABIAMY_PASS` Odrabiamy.pl password, 
    - `TG_TOKEN` Telegram bot token,
    - `DB_ADDRESS` PostgreSQL address,
    - `POSTGRES_USER` PostgreSQL user,
    - `POSTGRES_PASSWORD` PostgreSQL password,
    - `POSTGRES_DB` PostgreSQL database name,
    - `DB_TABLE` PostgreSQL table name (by default in `table.sql` it's specified as "baza"),
    - `DB_PORT` PostgreSQL port.
5. Run:
    - `python3 -m venv odrabiamy-venv`
    - `source odrabiamy-venv/bin/activate`
    - `pip install -r requirements.txt`
    - `pip install "python-telegram-bot[job-queue]"`
    - `playwright install-deps` (only if using a debian-based distro with apt)
    - `playwright install firefox`
    - `chmod a+x run.sh`

## Launching (docker)
1. To start the bot, cd into the bot directory and run `docker compose up -d` in that directory.
2. To stop the bot, cd into the bot directory and run `docker compose down` in that directory.

## Launching (bare-metal)
1. To start the bot, cd into the bot directory and run `./run.sh` in that directory.
2. To stop the bot, just press Ctrl-C until you're back at your shell prompt.

## Management (whitelist)
If you try to interact with the bot, it will reply with a message about contacting the administrator. also providing user's ID. the user has to give you this ID to get access to your instance of this bot - then insert it into `whitelist.txt` file located in the repository's folder - you can do that on the fly (you don't have to restart the bot every time you add a new user to the whitelist)<br>Lines with # at the start qualify as comments, IDs should be put in their own line without any unwanted characters besides numbers of course (duh), spaces etc...<h3 style="margin:0;padding:0;">Example `whitelist.txt`:</h3>
```
# A comment for example:
# ID below belongs to XYZ
1234567890
# John Smith
9876543215
# Elon Musk
6565656566
# Jeff Bezos
4323424324
# Bill Gates
9090678467
```

## Usage
Because Odrabiamy.pl is a polish service, this bot replies in Polish.<br>
People have 2 options (technically 4) to interact with the bot:
1. <strong>/start</strong> - bot will ask for a link, and will show a button list of: exercises from the chosen page, and beside them 2 options: "split" and "all"; when the exercise number is chosen, bot will send only the specified exercise; when "split" will be chosen, bot will seperate all exercises for every individual image; when "all" will be chosen, bot will send all exercises from this page in one image.<br>
<strong>/startf</strong> - basically the same as /start but forces the bot to download solutions directly from odrabiamy, rather than from a local database cache (you can use this for example if the image contents are corrupted).
2. <strong>/get</strong> - the get syntax is: /get `<URL to odrabiamy>`, and: if the link redirects to the whole page, bot will send the whole page; if the link redirects to a specific exercise, bot will send a specific exercise.<br>
<strong>/getf</strong> - basically the same as /start but forces the bot to download solutions directly from odrabiamy, rather than from a local database cache (you can use this for example if the image contents are corrupted).

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
- [X] full dockerization
- [ ] provide a user-friendly first-time run shell script (for bare-metal users)
- [ ] code clean-up
- [ ] more secure way of storing secrets

## Warning
Using odrabiamy.pl API with external programs, scripts is allowed only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is licensed under GNU General Public License Version 3.
See [LICENSE](https://github.com/NetMan134/odrabiamy-telegram/blob/master/LICENSE) for more information.
