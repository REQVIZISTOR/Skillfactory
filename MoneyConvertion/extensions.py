import requests
import json
from config import keys
class ConvertionException(Exception):
    pass

class CryptoConverter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionException(f'Невозможно перевести одинаковые валюты {base}.')

        quote_ticker = keys.get(quote)
        if not quote_ticker:
            raise ConvertionException(f'Не удалось обработать валюту {quote}')

        base_ticker = keys.get(base)
        if not base_ticker:
            raise ConvertionException(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionException(f'Не удалось обработать количество {amount}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        conversion_rate = json.loads(r.content)[base_ticker]

        total_base = amount * conversion_rate

        return total_base