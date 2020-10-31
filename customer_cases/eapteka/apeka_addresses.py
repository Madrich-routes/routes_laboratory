from returns.result import Result, safe
from typing import Tuple
from urllib.parse import urlencode

import pandas as pd
import requests


def main():
    data = pd.read_excel("eapteka_orders.xlsx")
    rows_count = len(data.index)
    res = []
    for i in range(rows_count):
        address = data.iloc[i]["АдресДоставки"]
        comment = data.iloc[i]["КомментарийКлиента"]

        if str(comment) != "nan":
            geocodeAddress, lot, lan = geocode(comment)
            if geocodeAddress == "":
                geocodeAddress, lot, lan = geocode(address)
        else:
            geocodeAddress, lot, lan = geocode(address)

        res.append([address, comment, geocodeAddress, lot, lan])
        print(f"Обработали уже {i} из {rows_count}")
    result_df = pd.DataFrame(
        res,
        columns=[
            "Адрес из Excel",
            "Коммент из Excel",
            "Адрес из геокодера",
            "Долгота",
            "Широта",
        ],
    )
    result_df.to_excel("eapteka_result.xlsx")
    i = 0


# @safe
def geocode(address: str) -> Tuple[int, int, int]:
    """
    Функция возвращает Result
    """
    url = f"http://search.maps.sputnik.ru/search/addr?q={urlencode(address)})"
    content = requests.get(url).json()

    features = content["result"]["address"][0]["features"][0]
    geocodeAddress = features["properties"]["display_name"]
    coord = features["geometry"]["geometries"][0]["coordinates"]
    lat, lon = float(coord[1]), str(coord[0])

    return geocodeAddress, lat, lon


if __name__ == "__main__":
    res = geocode('Москва, Земляной Вал, 38-40/15')
    print(res)
