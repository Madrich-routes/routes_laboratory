from collections import defaultdict

import pandas as pd

from geo.geocoding.others import yandex_api
from geo.geocoding.parsing import get_address
from geo.regions.job import check_moscow_region


def add_data(i, data, answer, was, be):
    place, city, lat, lng = answer
    data['id'].append(i)
    data['was'].append(was)
    data['corrected'].append(be)
    data['place'].append(place)
    data['city'].append(city)
    data['lat'].append(lat)
    data['lng'].append(lng)


def update_shit(orders_xl: pd.DataFrame):
    fail, done = 0, 0
    update = pd.read_excel('update.xlsx')
    data = defaultdict(list)

    for i, row in update.iterrows():

        if check_moscow_region(row['lat'], row['lng']):
            answer = (row['place'], row['city'], row['lat'], row['lng'])
            add_data(i, data, answer, row['was'], row['corrected'])
            continue

        print('index', i)

        client_address, client_comment = orders_xl['АдресДоставки'][i], orders_xl['КомментарийКлиента'][i]
        client_comment = '' if type(client_comment) == float else client_comment
        clear_address, clear_comment = get_address(client_address), get_address(client_comment)

        try:
            answer = yandex_api(clear_address)
            place, city, lat, lon = answer
            if check_moscow_region(lat, lon):
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
