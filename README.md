# hegai-bot
[![CircleCI](https://circleci.com/gh/Bot-Zavod/hegai_bot/tree/master.svg?style=svg)](https://circleci.com/gh/Bot-Zavod/hegai_bot/tree/master)

Heg.ai Telegram bot

## Enviroment
> python --version >>> Python 3.8.5
>
> linux version >>> Ubuntu 20.0

Telegram API wrapper used: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

On a AWS Ubuntu 18.04 new machine, below installations are required:

* `sudo apt-get install gcc libpq-dev`
* `sudo apt-get install python3-dev python3-pip python3-venv python3-wheel`
* `sudo apt install git-all`
* `pip3 install wheel`


## Launch
* `git clone --recurse-submodules https://repo.url repo` - clone repo
* `cd repo` - move to project directory
---
* `source setup.sh` - create and activate virtual environment, install dependencies
    * `--dev` or  `-d`  set up development environment with pre-commit formatter, [read more about pre-commit](https://pre-commit.com/#python)
* `cp .env.example .env` - create your .env file and insert your values
* `openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem` - create a self-signed SSL certificate for webhook, [read more about ssl for telegram](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#creating-a-self-signed-certificate-using-openssl)

* `python3 -m src.run` - run as python module from top src directory to acsess database layer
    * `--web-hook` or `-w`  run on webhook (polling by default)
    * `--debug` or `-d`  disable logging to telegram channel if you test locally
    * `--service` or `-s`  echo service msgs to any msg or commands
