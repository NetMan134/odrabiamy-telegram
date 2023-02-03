# odrabiamy-telegram
odrabiamy-telegram is a Telegram bot client for odrabiamy.pl

## Installation (dockerized python and postgresql)
1. clone this repository (`git clone https://github.com/NetMan134/odrabiamy-telegram`)
2. make sure you have docker and docker compose plugin installed on your system
3. go into the repository's folder
4. modify variables.env to your needs (mainly odrabiamy login, password and telegram bot token)
5. run `docker compose up -d` in that directory

### Updates
1. stop the instance by running `docker compose down`
2. run `git pull` to acquire new commits
3. run `docker compose up -d --build`

### Troubleshooting
If the containers behave uneven, try rebuilding them.
To do that, run: `docker compose down` and `docker compose up -d --build`

## Installation (bare-metal) 
1. set up a postgresql server (with a database and ability to read/write in a database table of course - you can create a docker container with a postgres image), and run a sql instruction from `table.sql` file
2. modify `./run.sh` to your needs (odrabiamy login, password, telegram bot token, postgresql address, postgresql user, postgresql password, postgresql database name, postgresql table name [by default it is "baza"], and postgresql port)
3. run:
    - `python3 -m venv odrabiamy-venv`
    - `source odrabiamy-venv/bin/activate`
    - `pip install -r requirements.txt`
    - `pip install "python-telegram-bot[job-queue]"`
    - `playwright install-deps` (only if using a debian-based distro with apt)
    - `playwright install firefox`
    - `chmod a+x run.sh`

## Launching (docker)
1. to start the bot, cd into the bot directory and run `docker compose up -d` in that directory
2. to stop the bot, cd into the bot directory and run `docker compose down` in that directory

## Launching (bare-metal)
1. to start the bot, cd into the bot directory and run `./run.sh` in that directory
2. to stop the bot, just press Ctrl-C until you're back at your shell prompt

## Management (whitelist)
If you try to interact with the bot, it will spit out a message about contacting the administrator (in polish for end-users friendliness, odrabiamy.pl is a polish service afterall) also providing user's ID. the user has to give you this ID to get access to your instance of this bot - then insert it into `whitelist.txt` file located in the repository's folder - you can do that on the fly (you don't have to restart the bot every time you add a new user to the whitelist)<br>Lines with # at the start qualify as comments, IDs should be put in their own line without any unwanted characters besides numbers of course (duh), spaces etc...<h3 style="margin:0;padding:0;">Example `whitelist.txt`:</h3>
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
People have 2 options (technically 4) to interact with the bot
1. <strong>/start</strong> - bot will ask for a link, and will show a button list of exercises from the chosen page and beside them 2 options: split and all. when the exercise number is chosen, bot will send only the specified exercise. when split will be chosen, bot will seperate all exercises from this page for every individual image. when all will be chosen, bot will send all exercises from this page in one image.<br>
<strong>/startf</strong> - basically the same as /start but forces download from odrabiamy than from a local database cache.
2. <strong>/get</strong> - the get syntax is: /get `<URL to odrabiamy>`, depending on if the link redirects to the whole page or a specific exercise, bot will send the whole page OR a specific exercise.<br>
<strong>/getf</strong> - basically the same as /get but forces download from odrabiamy than from a local database cache.

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
- [ ] provide a user-friendly first-time run shell script (for not using full dockerization)
- [ ] code clean-up
- [ ] more secure way of storing secrets

## Warning
Using odrabiamy.pl API with external programs, scripts is allowed only with administration consent.
User takes all the responsibility for their actions when using this program.

## License
This project is licensed under GNU General Public License Version 3.
See [LICENSE](https://github.com/NetMan134/odrabiamy-telegram/blob/master/LICENSE) for more information.
