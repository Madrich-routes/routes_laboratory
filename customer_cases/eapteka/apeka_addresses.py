import json

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
            geocodeAddress, lot, lan = get_coords(comment)
            if geocodeAddress == "":
                geocodeAddress, lot, lan = get_coords(address)
        else:
            geocodeAddress, lot, lan = get_coords(address)

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


def get_coords(address):
    map_request = "http://search.maps.sputnik.ru/search/addr?q={address})".format(
        address=address.replace(" ", "%20")
    )
    response = requests.get(map_request)
    content = json.loads(response.content)
    geocodeAddress, lot, lan = "", "", ""
    if len(content["result"]) > 1:
        coord = content["result"]["address"][0]["features"][0]["geometry"][
            "geometries"
        ][0]["coordinates"]
        lot = str(coord[1])
        lan = str(coord[0])
        geocodeAddress = content["result"]["address"][0]["features"][0]["properties"][
            "display_name"
        ]
    return geocodeAddress, lot, lan


if __name__ == "__main__":
    main()
