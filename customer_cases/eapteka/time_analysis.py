import os
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

array = np.ndarray

def make_windows_orders(interval: str) -> Tuple[int, int]:
    start, end = 0, 24
    tokens = interval.split(' ')
    size = len(tokens)

    for i, token in enumerate(tokens):
        if token == 'с' and i != size - 1:
            if tokens[i + 1]:
                start = int(tokens[i + 1][0:2])
        if token == 'по' and i != size - 1:
            if tokens[i + 1]:
                end_t = f'{tokens[i + 1]}' if 9 < int(tokens[i + 1][:2]) < 24 else f'23:59'
                end = int(end_t[0:2])

    return start, end


def statistic(tw):
    time_statistic, st = [0] * 24, {}

    for window in tw:
        start, end = window
        for i in range(start, end):
            time_statistic[i] += 1

    for i in range(24):
        st[f'{i}'] = time_statistic[i]
    return st


def statistic_answer(directory):
    pts, time_statistic, st = 0, [0] * 24, {}

    for csv in os.listdir(directory):
        file = directory + csv
        if '.ipynb_checkpoints' in file:
            continue
        answer = pd.read_csv(file)
        for i, row in answer.iterrows():
            if row['activity'] == 'delivery':
                pts += 1
                time_statistic[int(row['arrival'][11:13])] += 1

    print(pts)
    for i in range(24):
        st[f'{i}'] = time_statistic[i]
    return st


def st_show(information: dict):
    plt.bar(information.keys(), information.values())
    plt.show()


def show_statistic(couriers_dir: str):
    orders_inf = pd.read_excel('./data/Заказы_13.xlsx')

    time_windows = []
    for i, row in orders_inf.iterrows():
        time_windows.append(make_windows_orders(row['ИнтервалДоставки']))
    points_time_statistic = statistic(time_windows)
    st_show(points_time_statistic)

    couriers_data = pd.read_excel('./data/Курьеры_13.xlsx')

    time_windows = []
    for i, row in couriers_data.iterrows():
        start, end = row['Интервал работы'].split('-')
        time_windows.append((int(start), int(end)))
    couriers_time_statistic = statistic(time_windows)
    st_show(couriers_time_statistic)

    answer_time_statistic = statistic_answer(couriers_dir)
    st_show(answer_time_statistic)

    st = {}
    for i in range(24):
        points = points_time_statistic[str(i)]
        st[str(i)] = answer_time_statistic[str(i)] / points if points != 0 else 0
    st_show(st)

    st = {}
    for i in range(24):
        couriers = couriers_time_statistic[str(i)]
        st[str(i)] = answer_time_statistic[str(i)] / couriers if couriers != 0 else 0
    st_show(st)


show_statistic('./couriers/')
