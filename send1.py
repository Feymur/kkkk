import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc

import telebot
from telebot import types

import config
from create_db import Users

bot = telebot.TeleBot(config.TOKEN)


def send():
    engine = create_engine(config.db)

    Session = sessionmaker(bind=engine)
    session = Session()

    users = session.query(Users).all()

    for i in users:
        print(i)
        session.close()

send()
