import os

import bs4
import pandas as pd
import requests

from utils.logs import logger


def build_df(xml_url) -> pd.DataFrame:
    """Получаем датафрейм для всего метро."""
    logger.info('Составляю словарь станций метро...')
    df = parse_metro(xml_url)
    return df

def get_metro_xml(url: str):
    """Притворяемся браузером и получаем информацию по метро."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) G`ecko/20100101 Firefox/45.0'}
    s = requests.Session()
    r = s.get(url, headers=headers)
    return r.text

def parse_metro(xml_url_or_filename):
    """Парсим данные, которые нам отдает API метро."""
    if os.path.exists(xml_url_or_filename):
        print(f'Get XML from file: {xml_url_or_filename}')
        soup = bs4.BeautifulSoup(open(xml_url_or_filename).read(), 'lxml')
    else:
        print(f'Get XML from url: {xml_url_or_filename}')
        soup = bs4.BeautifulSoup(get_metro_xml(xml_url_or_filename), 'lxml')

    stations = soup.find('scheme', {'locale': 'ru'}).findAll('station')
    data = {}
    for station in stations:
        try:
            name = station.find('name').find('text').text
        except:
            try:
                name = int(station.find('name')['sameasforstation'])
            except:
                continue
            # name = int(re.sub(r"[^0-9.,]+", '', station.find('name').text))
        # print(station['id'])
        data[int(station['id'])] = {'coord': (
            float(station.find('geocoordinates')['latitude']), float(station.find('geocoordinates')['longitude'])),
            'name': name, 'links': {}}

    for id, item in data.items():
        if type(item['name']) == int:
            item['name'] = data[item['name']]['name']

    links = soup.find('scheme', {'locale': 'ru'}).find('links')
    for weight, link in zip(links.findAll('weight', {'type': 'time'}), links.findAll('link')):
        data[int(link['fromstation'])]['links'][int(link['tostation'])] = float(weight.text)
        data[int(link['tostation'])]['links'][int(link['fromstation'])] = float(weight.text)

    dataframe = pd.DataFrame.from_dict(data, orient='index')
    return dataframe.dropna()
