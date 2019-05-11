from datetime import datetime

from bs4 import BeautifulSoup
import requests


def main():
    data_url = 'https://finance.yahoo.com/quote/SPY/options'
    data_html = requests.get(data_url).content
    content = BeautifulSoup(data_html, 'html.parser')
    summary_table = []
    tables = content.find_all('table')
    for i in range(0, len(content.find_all('table'))):
        summary_table.append(tables[i])

    calling_option(summary_table)


def calling_option(option_tables):
    calls = option_tables[0].find_all('tr')[1:]
    itm_calls = []
    otm_calls = []

    for call_option in calls:
        if 'in-the-money' in str(call_option):
            itm_calls.append(call_option)
        else:
            otm_calls.append(call_option)

    itm_call = itm_calls[-1]
    otm_call = otm_calls[0]

    get_call_itm_info(itm_call)
    get_call_otm_info(otm_call)


def get_call_itm_info(itm_call):
    itm_call_data = []
    for td in BeautifulSoup(str(itm_call), 'html.parser').find_all('td'):
        itm_call_data.append(td.text)

    itm_call_info = {
        'contract': itm_call_data[0],
        'strike': itm_call_data[2],
        'last': itm_call_data[3],
        'bid': itm_call_data[4],
        'ask': itm_call_data[5],
        'volume': itm_call_data[8],
        'iv': itm_call_data[10]
    }
    print('======== itm-call-info ==========')
    print(itm_call_info)


def get_call_otm_info(otm_call):
    otm_call_data = []
    for td in BeautifulSoup(str(otm_call), 'html.parser').find_all('td'):
        otm_call_data.append(td.text)

    otm_call_data = {
        'contract': otm_call_data[0],
        'strike': otm_call_data[2],
        'last': otm_call_data[3],
        'bid': otm_call_data[4],
        'ask': otm_call_data[5],
        'volume': otm_call_data[8],
        'iv': otm_call_data[10]
    }
    print('======== otm-call-info ==========')
    print(otm_call_data)


if __name__ == '__main__':
    main()
