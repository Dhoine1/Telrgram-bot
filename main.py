import telebot
from extensions import APIException, ProcessingRequest
from config import money, TOKEN

bot = telebot.TeleBot(TOKEN)


# Обработка команд /help и /start
@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    text = '''/value - для получения списка валют.\n
    Для перевода одной валюты в другую введите:\n
    <валюту, которую нужно перевести> <в какую нужно перевести> <количество> \n
    Например: usd rub 10'''
    bot.reply_to(message, text)


# Обработка команды /value
@bot.message_handler(commands=['value'])
def send_value(message):
    text = 'Список валют: '
    for i in money:
        text += f'\n{i}: {money[i]}'
    bot.reply_to(message, text)


# Обработка присланного в чат текста
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:  # проверка корректности ввода
        if len(message.text.split(' ')) != 3:
            raise APIException('Неверное кол-во параметров')

        first, second, amount = message.text.split(' ')
        # Вызов функции из модуля extension, переводящего валюту
        itog = ProcessingRequest.get_price(first, second, amount)
    except APIException as e:   # вызов пользовательских исключений
        bot.reply_to(message, f"{e} \n Введите /help - для помощи")
    except Exception as e:  # вызов системных исключений
        bot.reply_to(message, f"Произошла какая-то ошибка \n {e}")
    else:  # Вывод в чат итогового тектса
        bot.send_message(message.chat.id, f"{amount} {first} = {itog} {second}")


bot.polling(none_stop=True)
