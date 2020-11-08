"""Временный модуль для остальных api.

Со временем его нужно будет разбить на куски.
"""
import herepy
from dask.bytes.tests.test_http import requests

YANDEX = ''
HERE = ''
eapteka_path = ''

geocoderApi = herepy.GeocoderApi('')

def here_api(address: str):
    """Геокодим через here."""
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
    """Геокодим через yandex."""
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
