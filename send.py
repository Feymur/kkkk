# !/usr/bin/python3
import config
import time
import schedule

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
    mes = '''\U0001F596Дорогой друг! Напоминаем!\n\n\U0001F4B0За КАЖДОГО приглашенного ты получаешь 0.5 рублей, на статусе "Декан" 1.5 рубля, это самый выгодный вариант для старта. Отзывы о нашей работе ты сможешь найти ниже\U0001F447\n\n\U0001F4AFСкоро вас ждут крутые и денежные конкурсы, а также много заданий, где вы сможете заработать свои первые деньги с нами\n\n\U0000260EОтзывы:\nhttps://vk.cc/arU1vF\n\n\U0001F468\U0001F4BBОфициальная тех. поддержка:\n@tp_youdream_bot'''
    for user in users:
        try:
            bot.send_message(user.chat_id, mes)
        except:
            users.remove(user)
    session.close()

schedule.every().day.at('18:00').do(send)

while True:
    schedule.run_pending()
    time.sleep(600)
