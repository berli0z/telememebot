# Telegram meme streamer

Telegram meme streamer is a basic python package that includes a chatbot to send **memes**, which have to be approved in a control private group. Once approved, they are passed to a **redis** database, and then populate both a google drive and a **flask API** . You will need some prior knowledge in order to deploy successfully.
![image](https://user-images.githubusercontent.com/40333748/103179092-d28adc80-4888-11eb-9c57-0049c3614186.png)


# Installation

Please remember to use python 3, i have tested this on Ubuntu 18, Raspbian (with some edits) and OSX.

## Git clone
```git clone https://github.com/berli0z/telememebot.git```

## Create virtualenv
First, install python-venv from apt/brew. Then:
```cd telememebot```
```virtualenv venv```
```source venv/bin/activate```

## Install requirements
```pip install -r requirements.txt```

## Install redis
Follow the online instructions for your system, then start with default config.

## Get your google keys

You will need some libraries and a script by google, you will need the key to edit gdrive. This is a bit tricky more info TBD.

## Prepare google drive

TBD

## Create telegram bot
TBD

## Get telegram chat ids

TBD

## Get your google token

TBD

## Edit config file

Open the ```sample_config.py``` file and fill in all the missing values, then rename it to ```config.py```.


# How to run

First, start the telegram bot with ```python app.py```, then start the api service with ```python api.py```.
You can use ```screen``` on an headless system to run both processes at once.
