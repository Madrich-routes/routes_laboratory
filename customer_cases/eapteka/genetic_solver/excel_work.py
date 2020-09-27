import os
from collections import defaultdict

import pandas as pd
from transliterate import translit


def save_excel(i, couriers_file, depots_file):
    writer = pd.ExcelWriter(f'solver_{i}_info.xlsx')
    couriers = pd.read_csv(couriers_file)
    depots = pd.read_csv(depots_file)
    couriers.to_excel(writer, sheet_name='couriers_info', index=False)
    depots.to_excel(writer, sheet_name='depots_info', index=False)
    writer.save()


def save_couriers(i, couriers_directory):
    writer = pd.ExcelWriter(f'solver_{i}_couriers.xlsx')
    for file in os.listdir(couriers_directory):
        if file == '.ipynb_checkpoints' or 'backup' in file:
            continue
        couriers = pd.read_csv(f'{couriers_directory}/{file}')
        couriers.to_excel(writer, sheet_name=file.replace('Мск,', '')[:31], index=False)
    writer.save()


def convert_excel(file):
    writer = pd.ExcelWriter(file)
    couriers_info = pd.read_excel(file, sheet_name='couriers_info')
    depots_info = pd.read_excel(file, sheet_name='depots_info')

    couriers = {}
    couriers_type = {}
    couriers_data = pd.read_excel('./data/Курьеры_13.xlsx')

    for i, row in couriers_data.iterrows():
        name = translit(f'{row["Сотрудник"]}', 'ru', reversed=True)
        cost = int(row['Стоимость 1 заказа'])
        couriers[name] = cost
        couriers_type[name] = row['Должность']

    couriers_summary = {}
    for i, row in couriers_info.iterrows():
        name = row['name']
        points = row['points']
        duration = row['duration']
        distance = row['distance']

        if name not in couriers_summary:
            couriers_summary[name] = {}
            couriers_summary[name]['type'] = couriers_type[name]
            couriers_summary[name]['points'] = points
            couriers_summary[name]['duration'] = duration
            couriers_summary[name]['distance'] = distance
        else:
            couriers_summary[name]['points'] += points
            couriers_summary[name]['duration'] += duration
            couriers_summary[name]['distance'] += distance

    tmp = defaultdict(list)
    for name, values in couriers_summary.items():
        tmp['name'].append(name)
        tmp['type'].append(values['type'])
        tmp['points'].append(values['points'])
        tmp['duration'].append(values['duration'])
        tmp['distance'].append(values['distance'])

    couriers_info.to_excel(writer, sheet_name='couriers_info', index=False)
    depots_info.to_excel(writer, sheet_name='depots_info', index=False)
    pd.DataFrame.from_dict(tmp).to_excel(writer, sheet_name='couriers_summary', index=False)
    writer.save()
