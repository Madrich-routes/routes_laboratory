# @safe
from typing import Tuple
from urllib.parse import urlencode

import requests


def geocode(address: str) -> Tuple[int, int, int]:
    """Функция возвращает Result."""
    url = f"http://search.maps.sputnik.ru/search/addr?q={urlencode(address)})"
    content = requests.get(url).json()

    features = content["result"]["address"][0]["features"][0]
    geocodeAddress = features["properties"]["display_name"]
    coord = features["geometry"]["geometries"][0]["coordinates"]
    lat, lon = float(coord[1]), str(coord[0])

    return geocodeAddress, lat, lon
