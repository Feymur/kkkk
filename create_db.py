from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import config

engine = create_engine(config.db)
metadata = MetaData()
Base = declarative_base()
 

class Users(Base):
    __tablename__ = 'users'
 
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    balance = Column(Integer, default=0)
    rank = Column(Integer, default=0) #rangs: 0 - new user, 1 - student, 2 - master, 3 - deccan
    step = Column(Integer)
    referals = Column(JSON, default={0:[], 1:[], 2:[]})
    refer = Column(Integer)

    def __init__(self, chat_id, step):
        self.chat_id = chat_id
        self.step = step

class Tranzactions(Base):
    __tablename__ = 'tranzactions'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    tranzactions = Column(JSON)
    amount = Column(Integer, default=0)

    def __init__(self, chat_id, tranzaction):
        self.chat_id = chat_id
        self.tranzactions = tranzaction



Base.metadata.create_all(engine)

