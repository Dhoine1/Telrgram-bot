import telebot
import sqlite3
import datetime
# import configparser
# from datetime import date, datetime
from extensions import APIException, ProcessingRequest
from config import money, TOKEN

bot = telebot.TeleBot(TOKEN)


# Обработка команд /help и /start
@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    text = '''/value - для получения списка валют.\n
    Для перевода одной валюты в другую введите:\n
    <валюту, которую нужно перевести> <в какую нужно перевести> <количество> \n
    Например: usd rub 10\n
    '''
    bot.reply_to(message, text)


# Обработка команды /value
@bot.message_handler(commands=['value'])
def send_value(message):
    text = 'Список валют: '
    for i in money:
        text += f'\n{i}: {money[i]}'
    bot.reply_to(message, text)


@bot.message_handler(commands=['event'])
def send_value(message):
    now_date = (datetime.datetime.now() + datetime.timedelta(days=1))
    text = f'Мероприятия на завтра: {now_date.strftime("%d-%m-%Y")}'

    connection = sqlite3.connect('\\\\192.168.3.116\infosys\infosys\db.sqlite3')
    cursor = connection.cursor()
    request = f'SELECT * FROM events_event as d WHERE d.data = "{now_date.strftime("%Y-%m-%d")}"'
    cursor.execute(request)
    events = cursor.fetchall()

    if not events:
        text += '\nЗавтра мероприятий нет.'
    else:
        for event in events:
            sql = f"SELECT m.hall_name FROM events_halls as m, events_event as p, events_location as cp" \
                  f" WHERE p.id = {event[0]} AND cp.event_id = p.id AND cp.hall_id = m.id"
            cursor.execute(sql)
            halls = cursor.fetchall()
            hall = ""
            for i in halls:
                for j in i: hall += f'{j},  '
            text += f'\n({event[3][:5]}-{event[4][:5]}) - {event[1]} \n Залы: {hall}\n-----'

    connection.close()
    bot.reply_to(message, text)


# @bot.message_handler(commands=['enter'])
# def send_value(message):
#     try:
#         config = configparser.ConfigParser()
#         config.read('R:/OvrsrAgent.ini')
#         count = int(config.get('Overseer', 'EventOrdNo'))
#         config.set('Overseer', 'EventOrdNo', f'{count + 1}')
#
#         with open('R:/OvrsrAgent.ini', 'w') as configfile:
#             config.write(configfile)
#
#         with open(f'R:/Ovrsr[{str(date.today()).replace("-", "")}].txt', 'a') as f:
#             f.write(f'{str(date.today()).replace("-", "")},{datetime.now().strftime("%H:%M:%S")},RTC,{count},5409041651212,ConfirmEnter,4260,Игнатьев Леонид,108\n')
#
#         with open(f'G:/SHOP/Overseer/Ovrsr[{str(date.today()).replace("-", "")}].txt', 'a') as f:
#             f.write(f'{str(date.today()).replace("-", "")},{datetime.now().strftime("%H:%M:%S")},RTC,{count},5409041651212,ConfirmEnter,4260,Игнатьев Леонид,108\n')
#
#         text = 'Вход выполнен'
#         bot.reply_to(message, text)
#     except Exception as e:
#         bot.reply_to(message, f"Произошла какая-то ошибка \n {e}")


# @bot.message_handler(commands=['leave'])
# def send_value(message):
#     try:
#         config = configparser.ConfigParser()
#         config.read('R:/OvrsrAgent.ini')
#         count = int(config.get('Overseer', 'EventOrdNo'))
#         config.set('Overseer', 'EventOrdNo', f'{count + 1}')
#
#         with open('R:/OvrsrAgent.ini', 'w') as configfile:
#             config.write(configfile)
#
#         with open(f'R:/Ovrsr[{str(date.today()).replace("-", "")}].txt', 'a') as f:
#             f.write(f'{str(date.today()).replace("-", "")},{datetime.now().strftime("%H:%M:%S")},RTC,{count},5409041651212,ConfirmLeave,4260,Игнатьев Леонид,107\n')
#
#         with open(f'G:/SHOP/Overseer/Ovrsr[{str(date.today()).replace("-", "")}].txt', 'a') as f:
#             f.write(
#                 f'{str(date.today()).replace("-", "")},{datetime.now().strftime("%H:%M:%S")},RTC,{count},5409041651212,ConfirmLeave,4260,Игнатьев Леонид,107\n')
#
#         text = 'Выход выполнен'
#         bot.reply_to(message, text)
#     except Exception as e:
#         bot.reply_to(message, f"Произошла какая-то ошибка \n {e}")


# Обработка присланного в чат текста
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:  # проверка корректности ввода
        if len(message.text.split(' ')) != 3:
            raise APIException('Неверное кол-во параметров')

        first, second, amount = message.text.split(' ')
        # Вызов функции из модуля extension, переводящего валюту
        itog = ProcessingRequest.get_price(first, second, amount)
    except APIException as e:  # вызов пользовательских исключений
        bot.reply_to(message, f"{e} \n Введите /help - для помощи")
    except Exception as e:  # вызов системных исключений
        bot.reply_to(message, f"Произошла какая-то ошибка \n {e}")
    else:  # Вывод в чат итогового тектса
        bot.send_message(message.chat.id, f"{amount} {first} = {itog} {second}")


bot.polling(none_stop=True)
