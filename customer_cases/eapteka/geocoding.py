from collections import defaultdict

import herepy
import pandas as pd
import requests

YANDEX = ''
HERE = ''
eapteka_path = ''

geocoderApi = herepy.GeocoderApi('')
orders_xl = pd.read_excel(eapteka_path + 'data/Заказы_13.xlsx')


def get_address(address):
    if not address:
        return None
    tokens = address.split(',')

    black_list = ['подъезд', 'код домофона', "эт", 'этаж', "кв", "квартира", "корп.", "корп ",
                  "позвонить", "код", "домофон", "пом", "дмф", "помещение", "п-д", ]
    white_list = ["Московская ", "улица ", "дом ", "д. ", "ул. ", "г. ",
                  "пр-кт ", "проспект ", ]

    address = []
    for token in tokens:
        if any(x in token for x in white_list):
            address.append(token)
            continue
        if any(x in token for x in black_list):
            continue
        address.append(token)
    address = ' '.join(address)
    return address


def here_api(address: str):
    if not address:
        return None
    response = geocoderApi.free_form(address)
    answer = response.as_dict()['items']
    if not answer:
        return None
    answer = answer[0]
    place = answer['title']
    city = answer['address']['city']
    lat = answer['position']['lat']
    lng = answer['position']['lng']
    return place, city, lat, lng


def yandex_api(address: str):
    if not address:
        return None
    r = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX}&format=json&' +
                     f'geocode={address}&results=1&bbox=54.966833,36.168665~56.393109,38.9163203')
    answer = r.json()['response']['GeoObjectCollection']["featureMember"]
    if not answer:
        return None
    answer = answer[0]['GeoObject']
    place = answer['metaDataProperty']['GeocoderMetaData']['text']
    city = answer['metaDataProperty']['GeocoderMetaData']['Address']['Components'][2]['name']
    lng, lat = answer['Point']['pos'].split(' ')
    return place, city, float(lat), float(lng)


def add_data(i, data, answer, was, be):
    place, city, lat, lng = answer
    data['id'].append(i)
    data['was'].append(was)
    data['corrected'].append(be)
    data['place'].append(place)
    data['city'].append(city)
    data['lat'].append(lat)
    data['lng'].append(lng)


def check(answer):
    place, city, lat, lng = answer
    if 54.966833 < lat < 56.393109 and 36.1686653 < lng < 38.9163203:
        return True
    return False


def try_this(lat, lon):
    if 54.966833 < lat < 56.393109 and 36.1686653 < lon < 38.9163203:
        return True
    return False


def update_shit():
    fail, done = 0, 0
    update = pd.read_excel('update.xlsx')
    data = defaultdict(list)

    for i, row in update.iterrows():

        if try_this(row['lat'], row['lng']):
            answer = (row['place'], row['city'], row['lat'], row['lng'])
            add_data(i, data, answer, row['was'], row['corrected'])
            continue

        print('index', i)

        client_address, client_comment = orders_xl['АдресДоставки'][i], orders_xl['КомментарийКлиента'][i]
        client_comment = '' if type(client_comment) == float else client_comment
        clear_address, clear_comment = get_address(client_address), get_address(client_comment)

        try:
            answer = yandex_api(clear_address)
            if answer is not None and check(answer):
                add_data(i, data, answer, client_address, clear_comment)
                done += 1
                print('update')
                continue

        except Exception as exc:
            print(id, exc)

        add_data(i, data, (row['place'], row['city'], row['lat'], row['lng']), row['was'], row['corrected'])
        print(client_address, '\n', client_comment)
        fail += 1

    pd.DataFrame.from_dict(data).to_excel("update_3.xlsx", index=False)
    print(done, fail)
    return data
