import requests
import json
import config
import db_func
import time
from create_db import Tranzactions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(config.db)

Session = sessionmaker(bind=engine)
session = Session()

def check_donate(user_id):

	api_access_token = config.qiwi_token
	my_login = config.qiwi_login

	s = requests.Session()
	s.headers['authorization'] = 'Bearer ' + api_access_token  
	parameters = {'rows': '10'}
	h = s.get('https://edge.qiwi.com/payment-history/v1/persons/'+my_login+'/payments', params = parameters)
	j = json.loads(h.text)

	for i in j['data']:
		tr_id = i['txnId']
		tr_id = str(tr_id)
		tr_type = i['type']
		status = i['status']
		amount = i['sum']['amount']
		currency = i['sum']['currency']
		comment = i['comment']
		if status == 'SUCCESS': status = True
		else: status = False
		if tr_type == 'IN': tr_type = True
		else: tr_type = False
		# if currency == 643: currency = 'rub'
		# elif currency == 840: currency = 'usd'

		if str(user_id) == comment and status and tr_type:
			# res = session.query(Tranzactions).filter(Tranzactions.tranzaction == user_id).scalar() is None
			
			# if res:
			# 	session.add(Tranzactions(user_id, {tr_id: {'date': time.ctime(time.time()), 'amount': amount}}))
			# 	session.commit()
			# 	return amount
			# else:
			res = session.query(Tranzactions).filter(Tranzactions.tranzactions == user_id).first()
			if tr_id not in res.tranzactions.keys():
				res.tranzactions[tr_id] = {'date': time.ctime(time.time()), 'amount': amount}
				db_func.add_many_parametrs(Tranzactions, user_id, {'tranzactions': res.tranzactions})

				return amount
			else:
				return False

	return False