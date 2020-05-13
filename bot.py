import telebot
from telebot import types

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc

import config
from create_db import Users, Tranzactions
import qiwi
from add_func import add_new_user, add_parametr, add_many_parametr_to_user


bot = telebot.TeleBot(config.TOKEN)

engine = create_engine(config.db)

Session = sessionmaker(bind=engine)
session = Session()

ranks = {
0: {'name': 'новичок', 'price': 0, 'ref_price': 50},
1: {'name': 'студент', 'price': 9900, 'ref_price': 75},
2: {'name': 'магистр', 'price': 15900, 'ref_price': 100},
3: {'name': 'декан', 'price': 25900, 'ref_price': 150}
}


#клавиатуры

main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_keyboard.add(
types.KeyboardButton(text='\U0001F4BC Личный кабинет'),
types.KeyboardButton(text='\U0001F4EC Отзывы'),
types.KeyboardButton(text='\U0001F91D Реферальная система')
)
	
donate = types.InlineKeyboardMarkup()
donate.add(
types.InlineKeyboardButton(text='Qiwi', url=config.qiwi_url)
)

check = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
check.add(
types.KeyboardButton(text='Проверить'),
types.KeyboardButton(text='Назад')
)

exit = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
exit.add(
types.KeyboardButton(text='выход')
)

lk = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
lk.add(
types.KeyboardButton(text='Внести'),
types.KeyboardButton(text='Вывести'),
types.KeyboardButton(text='Повышение статуса')
)
lk.add(types.KeyboardButton(text='Назад'))

shop = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
shop.add(
types.KeyboardButton(text='Студент'),
types.KeyboardButton(text='Магистр'),
types.KeyboardButton(text='Декан'),
types.KeyboardButton(text='Назад')
)


def give_money_to_refers(money, ref_id):
	for i in [0.1, 0.07, 0.05]:
		refer = session.query(Users).filter(Users.chat_id == ref_id).first()
		real_money = money * i
		add_parametr(ref_id, 'balance', refer.balance + int(real_money))
		bot.send_message(ref_id, f'Ты получил {real_money/100} р за реферала.')
		if refer.refer == 0:
			return 1
		ref_id = refer.refer
			
def number_of_referals(d):
	# n = 0
	# for k in d.keys():
	# 	n += len(d[k])
	return len(d['0'])

def number_of_levels(d):
	s = f'''
	1 уровень: {len(d['0'])} пользователей
	2 уровень: {len(d['1'])} пользователей
	3 уровень: {len(d['2'])} пользователей
	'''
	return s

def create_keyboard(text, rand=True, exit=False):
	if rand: random.shuffle(text)
	keyboard = types.ReplyKeyboardMarkup(row_width=len(text), resize_keyboard=True)
	for i in text:
		keyboard.add(i)
	if exit: keyboard.add('выход')
	return keyboard

@bot.message_handler(commands=['money'])
def admin_money(message):
	if message.chat.id == config.admin_id:
		l = message.text.split(' ')
		if l[0] == '/money':
			try:
				i = int(l[1])
				b = session.query(Users).filter(Users.chat_id == i).first()
				add_parametr(i, 'balance', b.balance - int(l[2])*100)
				bot.send_message(config.admin_id, f'{i} р было списано у пользователя {i}')
				bot.send_message(i, f'Ты вывел {l[2]} р')
			except:
				bot.send_message(config.admin_id, 'Command error.\n`\\money id сумма`', parse_mode= 'Markdown')


#Регистрация нового пользователя
@bot.message_handler(commands=['start'])
def registration(message):
	res = session.query(Users).filter(Users.chat_id == message.chat.id).scalar() is None
	if res:
		add_new_user(message.chat.id, 4)
		if message.text[7:] not in ['', str(message.chat.id)]:
			
			try:
				add_parametr(message.chat.id, 'refer', int(message.text[7:]))
			except:
				add_parametr(message.chat.id, 'refer', 0)
			try:
				ref_id = int(message.text[7:])
				refer = session.query(Users).filter(Users.chat_id == ref_id).first()
				refer.referals['0'].append(message.chat.id)
				add_parametr(ref_id, 'referals', refer.referals)
				money = ranks[refer.rank]['ref_price']
				add_parametr(ref_id, 'balance', refer.balance + money)
				bot.send_message(ref_id, f'Ты получил {money/100} р за реферала.')
				if refer.refer != 0:
					give_money_to_refers(money, refer.refer)
					for i in range(1, 3):
						if refer.refer == 0:
							break
						refer = session.query(Users).filter(Users.chat_id == refer.refer).first()
						refer.referals[str(i)].append(message.chat.id)
						add_parametr(refer.chat_id, 'referals', refer.referals)

			except:
				print('Invalid ref_id')
		else:
			add_parametr(message.chat.id, 'refer', 0)
		mes = 'YouDream - бот, который прокачает тебя и сделает богаче.\n\n\U0001F91DПриветствую тебя мой друг!\n\n\U0001F4B0С помощью нашего бота можно хорошо заработать! Приглашайте друзей и зарабатывайте деньги!\n\n\U0000231BСкоро будут множество интересных заданий и конкурсов, оставайся с нами!'
		bot.send_message(message.chat.id, mes, reply_markup=main_keyboard)

	else:
		add_parametr(message.chat.id, 'step', 4)
		bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_keyboard)


@bot.message_handler(commands=['back'])
def registration(message):
	try:
		user = session.query(Users).filter(Users.chat_id == message.chat.id).first()
		add_parametr(message.chat.id, 'step', 4)
		bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_keyboard)
	except:
		pass


@bot.message_handler(content_types = ['text'])
def main(message):

	try:
		user = session.query(Users).filter(Users.chat_id == message.chat.id).first()
		step = user.step
		balance = user.balance
	except:
		bot.send_message(message.chat.id, 'Зарегистрируйтесь!!! Для это воспользуйтесь командой /start')
		return 0

#user's office
	if step == 4 and message.text == '\U0001F4BC Личный кабинет':
		mes = f'''
		\U0001F4BC Личный кабинет

		\U0001F4B0 Баланс: {user.balance/100} р

		\U0001F91D Приглашено: {number_of_levels(user.referals)}
		
		\U0001F393 Статус: {ranks[user.rank]['name'].capitalize()}

		Реферальная ссылка: t.me/{config.name}?start={message.chat.id}
		'''
		bot.send_message(message.chat.id, mes, reply_markup=lk)


#ref_system
	elif step == 4 and message.text == '\U0001F91D Реферальная система':
		mes = '''
		\U0001F6A9 3 уровня на глубину:

		— 1 ур. — 5% за любое действие реферала (покупка статуса, выполнение заданий, приглашение рефералов)

		— 2 ур. — 7% за любое действие реферала (покупка статуса, выполнение заданий, приглашение рефералов)

		— 3 ур. — 10% за любое действие реферала (покупка статуса, выполнение заданий, приглашение рефералов)

		\U0001F393 3 статуса для повышения вознаграждения:

    	По умолчанию для всех новичков: вознаграждение 0.5 рубля

		— Студент — 0.75 за реферала — цена 99 рублей

		— Магистр — 1 за реферала — 159 рублей

		— Декан — 1.5 за реферала — 259 рублей
		'''
		bot.send_message(message.chat.id, mes)

#start shop
	elif step == 4 and message.text == 'Повышение статуса':
		mes = f'''Здесь ты можешь повысить свой статус:
		— Студент — 0.75 за реферала — цена 99 рублей

		— Магистр — 1 за реферала — 159 рублей

		— Декан — 1.5 за реферала — 259 рублей

		\U0001F4B0 Баланс: {user.balance/100} р
		'''
		add_parametr(message.chat.id, 'step', 8)
		bot.send_message(message.chat.id, mes, reply_markup=shop)


#use the buttons
	elif step == 4 and message.text not in ['\U0001F4BC Личный кабинет', '\U0001F91D Реферальная система', '\U0001F4EC Отзывы', 'Назад', 'Внести', 'Повышение статуса']:
		bot.send_message(message.chat.id, 'Используй кнопки', reply_markup=main_keyboard)

#back
	elif step in [4, 5] and message.text == 'Назад':
		add_parametr(message.chat.id, 'step', 4)
		bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_keyboard)
		
#suport
	elif step == 4 and message.text == '\U0001F4EC Отзывы':
		bot.send_message(message.chat.id, 'Здесь ты можешь оставить свой отзыв:\nhttps://vk.com/topic-193425879_40701274')

#donate
	elif step == 4 and message.text == 'Внести':
		add_parametr(message.chat.id, 'step', 5)
		bot.send_message(message.chat.id, f'''
		Цены на повышение статуса:

		— Студент — 0.75 за реферала — цена 99 рублей

		— Магистр — 1 за реферала — 159 рублей

		— Декан — 1.5 за реферала — 259 рублей

		Можно оплатить с банковской карты через Qiwi. Также можно оплатить через терминал или с номера мобильного телефона, выбрав Qiwi.
		Выбери способ оплаты.
		''', parse_mode= 'Markdown', reply_markup=donate)
		bot.send_message(message.chat.id, 'Комментарий к платежу(или деньги не придут):')
		bot.send_message(message.chat.id, str(message.chat.id))
		bot.send_message(message.chat.id, 'После оплаты нажми проверить.', reply_markup=check)

	if step == 5 and message.text == 'Проверить':
		res = qiwi.check_donate(message.chat.id)
		if res:
			bot.send_message(message.chat.id, f'Зачислено {res} р.', reply_markup=types.ReplyKeyboardRemove())
			add_parametr(message.chat.id, 'balance', balance + res*100)
			add_parametr(message.chat.id, 'step', 4)
			bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_keyboard)
		else:
			bot.send_message(message.chat.id, 'Возможно платёж ещё не прошёл. Попробуйте через минуту. Для выхода в главное меню напишите выход.\nЕсли возникли проблемы, пишите в поддержку')
	
	if step == 4 and message.text == 'Вывести':
		mes = '''
		Условия для вывода средств:

		— Минимум 3 приглашения 1-ого уровня

		— Для новичков и студентов: 3 рубля

		— Для остальных: 30 рублей

		\U00002757 Для вывода напиши сумму в рублях и номер qiwi кошелька.

		Для выхода нажмите /back'''
		bot.send_message(message.chat.id, mes, reply_markup=types.ReplyKeyboardRemove())
		bot.send_message(message.chat.id, 'Введите сумму в рублях:')
		add_parametr(message.chat.id, 'step', 6)
	
	if step == 6:
		flag = False
		if number_of_referals(user.referals) >= 3:
			if user.rank in [0, 1] and balance >= 300:
				flag = True
			elif user.rank in [2, 3] and balance >= 3000:
				flag = True
			else:
				flag = False
				bot.send_message(message.chat.id, 'У вас недостаточно денег или приглашённых пользователей.', reply_markup=main_keyboard)
				add_parametr(message.chat.id, 'step', 4)
		else:
			flag = False
			bot.send_message(message.chat.id, 'У вас недостаточно денег или приглашённых пользователей.', reply_markup=main_keyboard)
			add_parametr(message.chat.id, 'step', 4)
			
		if message.text.isdigit() and flag:
			session.query(Tranzactions).filter(Tranzactions.chat_id == message.chat.id).update({'amount': int(message.text)}, synchronize_session='evaluate')
			session.commit()
			add_parametr(message.chat.id, 'step', 66)
			bot.send_message(message.chat.id, 'Введите номер qiwi кошелька:')
		elif flag:
			bot.send_message(message.chat.id, 'В этом сообщении должны быть только цифры')

	if step == 66 and message.text:
		row = session.query(Tranzactions).filter(Tranzactions.chat_id == message.chat.id).first()
		bot.send_message(message.chat.id, 'Ваша заявка направлена на обработку модератору. Обработка может занять до 3-ёх дней.', reply_markup=main_keyboard)
		bot.send_message(config.admin_id, f'Заявка на вывод от пользователя {message.chat.id}\nqiwi: {message.text}\nсумма: {row.amount}')
		bot.send_message(config.admin_id, f'/money {message.chat.id} {row.amount}')
		add_parametr(message.chat.id, 'step', 4)


#shop
	if step == 8:
		if message.text == 'Назад':
			add_parametr(message.chat.id, 'step', 4)
			bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_keyboard)
		elif message.text == 'Студент':
			if balance < 9900:
				bot.send_message(message.chat.id, 'Недостаточно средств')
			elif user.rank >= 1:
				bot.send_message(message.chat.id, 'Ты уже студент или выше.')
			else:
				add_parametr(message.chat.id, 'rank', 1)
				add_parametr(message.chat.id, 'step', 4)
				give_money_to_refers(9900, user.refer)
				bot.send_message(message.chat.id, 'Поздравляю, теперь ты студент.', reply_markup=main_keyboard)
		elif message.text == 'Магистр':
			if balance < 15900:
				bot.send_message(message.chat.id, 'Недостаточно средств')
			elif user.rank >= 2:
				bot.send_message(message.chat.id, 'Ты уже магистр или выше.')
			else:
				add_parametr(message.chat.id, 'rank', 2)
				add_parametr(message.chat.id, 'step', 4)
				give_money_to_refers(15900, user.refer)
				bot.send_message(message.chat.id, 'Поздравляю, теперь ты магистр.', reply_markup=main_keyboard)
		elif message.text == 'Декан':
			if balance < 25900:
				bot.send_message(message.chat.id, 'Недостаточно средств')
			elif user.rank >= 3:
				bot.send_message(message.chat.id, 'Ты уже декан.')
			else:
				add_parametr(message.chat.id, 'rank', 3)
				add_parametr(message.chat.id, 'step', 4)
				give_money_to_refers(25900, user.refer)
				bot.send_message(message.chat.id, 'Поздравляю, теперь ты декан.', reply_markup=main_keyboard)


if __name__ == '__main__':
	bot.polling(none_stop = True)
