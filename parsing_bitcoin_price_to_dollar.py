
import requests
from bs4 import BeautifulSoup
import psycopg2


connect = psycopg2.connect(database='tickets', user='arlen', host='localhost', password=1)
cursor = connect.cursor()


def parse_bitok():
    url = "https://www.google.com/finance/quote/BTC-USD?sa=X&ved=2ahUKEwjZz4yi576BAxV6VfEDHZmZDREQ-fUHegQIGhAf"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    currency_element = soup.find('div', class_='AHmHk')
    currency_text = currency_element.text.strip()
    currency_text = currency_text.replace(',', '')
    currency_float = float(currency_text)
    print(f"Курс биткоина: {currency_float}$")
    print('Сохранено в базу данных')
    return currency_float


currency_rate = parse_bitok()

rate = currency_rate

cursor.execute('INSERT INTO bilets_bitrate (rate) VALUES (%s) ON CONFLICT (rate) DO UPDATE SET rate = EXCLUDED.rate', (rate,))

connect.commit()
connect.close()