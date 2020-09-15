import requests, json
import pandas as pd
import pickle5 as pickle
import numpy as np

# читаем входной файл
with open("addresses_excel.pkl", "rb") as f:
    data = pickle.load(f)

# подготавливаем результирующий словарь
result = {}
errors = 0
rows_count = len(data.index)

print(
    "Старт обработки, всего нужно обработать {count}, строк.".format(count=rows_count)
)

# проходим по всем строкам
try:
    for i in range(rows_count):
        # Обрабатываем адрес погрузки, приводим к строке, удаляем лишнюю инфу
        adr1 = data.iloc[i, 1:16].to_list()
        strAdr1 = " ".join([str(x) for x in adr1 if str(x) != "nan"])
        start = strAdr1.find("(")
        # end = strAdr1.find( ')' )
        if start != -1:  # and end != -1
            strAdr1 = strAdr1[0:start]  # + strAdr1[end+1:]

        # если такого адреса не было у нас - делаем запрос
        if not strAdr1 in result:
            map_request = "http://search.maps.sputnik.ru/search/addr?q={address})".format(
                address=strAdr1.replace(" ", "%20")
            )
            response = requests.get(map_request)
            content = json.loads(response.content)

            # если адрес получили - записываем координаты, в противном случае - пустые строки
            if len(content["result"]) > 1:
                coord = content["result"]["address"][0]["features"][0]["geometry"][
                    "geometries"
                ][0]["coordinates"]
                result[strAdr1] = (str(coord[1]), str(coord[0]))
            else:
                result[strAdr1] = ("", "")
                print("------- пустой адрес ------ " + strAdr1)
                errors += 1

        # повторяем все те же действия для адреса разгрузки
        adr2 = data.iloc[i, 17:35].to_list()
        strAdr2 = " ".join([str(x) for x in adr2 if str(x) != "nan"])
        start = strAdr2.find("(")
        # end = strAdr2.find( ')' )
        if start != -1:  # and end != -1
            strAdr2 = strAdr2[0:start]  # + strAdr2[end+1:]

        if not strAdr2 in result:
            map_request = "http://search.maps.sputnik.ru/search/addr?q={address})".format(
                address=strAdr2.replace(" ", "%20")
            )
            response = requests.get(map_request)
            content = json.loads(response.content)

            if len(content["result"]) > 1:
                coord = content["result"]["address"][0]["features"][0]["geometry"][
                    "geometries"
                ][0]["coordinates"]
                result[strAdr2] = (str(coord[1]), str(coord[0]))
            else:
                result[strAdr2] = ("", "")
                print("------- пустой адрес ------ " + strAdr2)
                errors += 1
        print("Обработали уже {} из {}".format(i, rows_count))
except Exception:
    print(Exception.args)

# сохраняем результат
result_df = pd.DataFrame.from_dict(result, orient="index")
result_df.to_excel("res.xlsx")
print("Обработка завершена, всего ошибок: {err}".format(err=errors))
