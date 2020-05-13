from create_db import Users, Tranzactions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time

import config


engine = create_engine(config.db)

Session = sessionmaker(bind=engine)
session = Session()

def add_new_user(chat_id, step):
	session.add(Users(chat_id, step))
	session.add(Tranzactions(chat_id, {}))
	session.commit()

def add_parametr(chat_id, parametr, value, step_plus=False, table=False):
	if not table:
		if step_plus:
			session.query(Users).filter(Users.chat_id == chat_id).update({Users.step: Users.step + 1}, synchronize_session='evaluate')
		session.query(Users).filter(Users.chat_id == chat_id).update({parametr: value}, synchronize_session='evaluate') 
	elif table:
		session.query(table).filter(table.chat_id == chat_id).update({parametr: value}, synchronize_session='evaluate')

	session.commit()

def add_many_parametr_to_user(chat_id, parametrs):
	for parametr in parametrs.keys():
		session.query(Users).filter(Users.chat_id == chat_id).update({parametr: parametrs[parametr]}, synchronize_session='evaluate')
	session.commit()