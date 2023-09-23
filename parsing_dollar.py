
import requests
from bs4 import BeautifulSoup
import psycopg2


connect = psycopg2.connect(database='tickets', user='arlen', host='localhost', password=1)
cursor = connect.cursor()


def parse_currency():
    url = "https://www.akchabar.kg/ru/exchange-rates/dollar/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    currency_element = soup.find('div', class_='nbkr_tabs_wrapper')
    usd_rate_text = currency_element.find('h2').text
    usd_rate_text = usd_rate_text.strip().replace(',', '.')

    if usd_rate_text:
        usd_rate = float(usd_rate_text)
        print("Курс доллара:", usd_rate)
        print("Данные сохранены в базу данных")
    return usd_rate

usd_rate = parse_currency()

rate = usd_rate

cursor.execute('INSERT INTO bilets_usdrate (rate) VALUES (%s) ON CONFLICT (rate) DO UPDATE SET rate = EXCLUDED.rate', (rate,))

connect.commit()
connect.close()

