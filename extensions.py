import requests
import json
from config import money


class APIException(Exception):
    pass


# Основной класс чата
class ProcessingRequest:
    @staticmethod
    def get_price(base, quote, amount):
        # Три исключения на корректность ввода данных
        if str.upper(base) not in money.values():
            raise APIException(f'Валюта {base} не найдена')

        if str.upper(quote) not in money.values():
            raise APIException(f'Валюта {quote} не найдена')

        if not amount.isdigit():
            raise APIException('Вводите корректное кол-во валюты')

        # Запрос к API Центробанка
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = json.loads(r.content)
        # Центробанк возвращает все курсы относительно рубля. Поэтому нужна проверка,
        # что введеная валюта не рубль. Иначе курс подставляется равным 1.
        if str.upper(base) == "RUB":
            currency_first = 1
        else:
            currency_first = data['Valute'][str.upper(base)]['Value']

        if str.upper(quote) == "RUB":
            currency_second = 1
        else:
            currency_second = data['Valute'][str.upper(quote)]['Value']

        # Вычисление отношения валют друг к другу, на основании их курса к рублю.
        itog = round((currency_first / currency_second) * float(amount), 2)
        return itog
