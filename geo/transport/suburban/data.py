import pickle as pkl

import numpy as np
import pandas as pd
from tqdm import tqdm
from yandex_rasp import YandexRasp

from utils.logs import logger


def build_df(all_uids_file, all_pathes_file) -> pd.DataFrame:
    """Получаем датафрейм для всего пригородного транспорта."""
    logger.info('Составляю словарь станций пригородных поездов и автобусов...')
    df = parse_suburban(all_uids_file=all_uids_file, all_pathes_file=all_pathes_file)
    return df

def parse_suburban(
        all_uids_file=None,
        all_pathes_file=None,
        MOW_CENTER=(55.73, 37.54),
        TOKEN='f667814b-8196-4041-a9ac-3a34518bce61',
        DOMEN='evgps.me'
):
    rasp = YandexRasp(TOKEN, DOMEN)
    # Get all stations in 50km from center of the city
    all_stations = rasp.nearest_stations(
        lat=MOW_CENTER[0],
        lng=MOW_CENTER[1],
        distance=50.0,
        transport_types=['bus'],
        station_types=['bus_stop'],
        lang="ru_RU",
        offset=0,
        limit=500_000,
        format="json")

    # Find all threads
    if all_uids_file:
        all_uids = np.load(all_uids_file)
    else:
        all_uids = []
        for station in tqdm(all_stations['stations']):
            shedule = rasp.station_schedules(
                station['code'],
                date=None,
                transport_types=['bus'],
                event='departure',
                lang="ru_RU",
                format="json",
                result_timezone=None,
                show_systems='yandex',
                coding_system='yandex'
            )
            for thread in shedule['schedule']:
                all_uids += [thread['thread']['uid']]
            all_uids = list(set(all_uids))

    # Find all pathes from uid
    if all_pathes_file:
        all_pathes = pkl.load(open(all_pathes_file, 'rb'))
    else:
        all_pathes = []
        for uid in tqdm(all_uids):
            # print(station)
            path = rasp.thread_path(uid=uid, from_=None, to=None, date=None, show_systems="yandex", lang="ru_RU",
                                    format="json")
            all_pathes.append(path)

    # Join nearest stations
    data = {
        station['code']: {
            'coord': [float(station['lat']), float(station['lng'])],
            'name': station['title'],
            'links': {},
        }
        for station in tqdm(all_stations['stations'])
    }

    for path in tqdm(all_pathes):
        for first_stop, second_stop in zip(path['stops'][:-1], path['stops'][1:]):
            fromstation = first_stop['station']['code']
            tostation = second_stop['station']['code']
            if fromstation not in data.keys():
                data[fromstation] = {'coord': None, 'name': first_stop['station']['title'], 'links': {}}
            data[fromstation]['name'] = first_stop['station']['title']
            data[fromstation]['links'][tostation] = float(second_stop['duration'] - first_stop['duration'])

    dataframe = pd.DataFrame.from_dict(data, orient='index')
    return dataframe.dropna()
