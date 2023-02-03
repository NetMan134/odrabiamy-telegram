FROM python:3.11.1
WORKDIR /odrabiamy-bot
COPY . .
RUN python3 -m venv odrabiamy-venv \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "python-telegram-bot[job-queue]" \
    && playwright install-deps \
    && playwright install firefox
CMD [ "python", "/odrabiamy-bot/odrabiamy-bot-telegram.py" ]
