import gzip

import mpu
import pandas as pd
import pickle5 as pickle

res = []
data = pd.read_excel("../data/data.xlsx")
coords_df = pd.read_csv("../data/coordinates.csv", sep=";").reset_index()
coords_df["matrix_id"] = coords_df.index
matrix = pickle.load(gzip.open("../data/res_matrix.pkl.gz", "rb"))

rows_count = len(data.index)

for i in range(rows_count):
    data_row = data.iloc[i, :].to_list()
    s_date = data_row[1].strftime("%d.%m.%Y") + " " + str(data_row[2])
    e_date = data_row[3].strftime("%d.%m.%Y") + " " + str(data_row[4])

    s_address = " ".join([str(x) for x in data_row[9:25] if str(x) != "nan"])
    start = s_address.find("(")
    if start != -1:
        s_address = s_address[0:start]
    e_address = " ".join([str(x) for x in data_row[25:43] if str(x) != "nan"])
    start = e_address.find("(")
    if start != -1:
        e_address = e_address[0:start]
    car = data_row[7]

    search = " ".join(s_address.split(" ")[1:]) if s_address[0].isdigit() else s_address
    s_row = coords_df.loc[coords_df["address"] == search]
    s_lat = float(s_row["0"])
    s_lon = float(s_row["1"])
    s_matr_id = int(s_row["matrix_id"])
    s_coord = "{0:.6f}".format(s_lat) + " " + "{0:.6f}".format(s_lon)
    s_index = coords_df.index[coords_df["address"] == search].to_list()[0]

    search = " ".join(e_address.split(" ")[1:]) if e_address[0].isdigit() else e_address
    e_row = coords_df.loc[coords_df["address"] == search]
    e_lat = float(e_row["0"])
    e_lon = float(e_row["1"])
    e_matr_id = int(e_row["matrix_id"])
    e_coord = "{0:.6f}".format(e_lat) + " " + "{0:.6f}".format(e_lon)
    e_index = coords_df.index[coords_df["address"] == search].to_list()[0]

    matrix_dist = matrix[s_index, e_index]
    linear_dist = mpu.haversine_distance((s_lat, s_lon), (e_lat, e_lon)) * 1000
    res.append(
        [
            s_date,
            e_date,
            s_address,
            e_address,
            s_coord,
            e_coord,
            s_matr_id,
            e_matr_id,
            linear_dist,
            matrix_dist,
            car,
        ]
    )
    print(f"Обработали уже {i} из {rows_count}")

result_df = pd.DataFrame(
    res,
    columns=[
        "Время погрузки",
        "Время разгрузки",
        "Адрес погрузки",
        "Адрес разгрузки",
        "Координаты погрузки",
        "Координаты разгрузки",
        "s_id",
        "e_id",
        "Расстояние по прямой, м",
        "Расстояние по матрице, м",
        "Машина",
    ],
)
result_df.to_excel("../data/pretty_result.xlsx")

# a = '141870, Московская обл, Дмитровский р-н, Зараменье д, дом № 41, строение 1'
# b = '350059, Краснодарский край, Краснодар г, Новороссийская ул, дом № 234'
