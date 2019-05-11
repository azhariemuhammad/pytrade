from datetime import datetime

from bs4 import BeautifulSoup
import requests


def main():
    data_url = 'https://finance.yahoo.com/quote/ANTM.JK'
    data_html = requests.get(data_url).content
    content = BeautifulSoup(data_html, 'html.parser')
    summary_table = []
    tables = content.find_all('table')
    quote = content.find_all('h1')[0].text[:7]
    print('======== Quote ==========')
    print(quote)
    for i in range(0, len(content.find_all('table'))):
        summary_table.append(tables[i])

    find_table(summary_table)


def find_table(summary_table):
    stock_data = summary_table[0].find_all('tr')[1:]
    get_summary(stock_data)

def get_summary(data):
    items = []
    for td in BeautifulSoup(str(data), 'html.parser').find_all('td'):
        items.append(td.text)

    summary = {
        'open': items[1],
        'bid': items[3],
        'ask': items[5],
        'day_range': items[7],
        'yoy_range': items[9],
        'volume': items[11],
        'avg_volume': items[13]
    }
    print(summary)

if __name__ == '__main__':
    main()
