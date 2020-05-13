from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc

import config
from create_db import Users, Tranzactions
from add_func import add_new_user, add_parametr, add_many_parametr_to_user


engine = create_engine(config.db)

Session = sessionmaker(bind=engine)
session = Session()

u = session.query(Users).all()
for i in u:
	session.add(Tranzactions(i.chat_id, {}))
session.commit()
session.close()
