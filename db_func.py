from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config


engine = create_engine(config.db)

Session = sessionmaker(bind=engine)
session = Session()


def add_many_parametrs(table, chat_id, parametrs):
	for parametr in parametrs.keys():
		session.query(table).filter(table.chat_id == chat_id).update({parametr: parametrs[parametr]}, synchronize_session='evaluate')
	session.commit()