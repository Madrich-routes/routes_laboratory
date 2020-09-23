from collections import defaultdict

import pandas as pd
import ujson

orders_file, clear_orders_file = './data/eapteka_result.xlsx', './data/Заказы_13.xlsx'
orders_lx = pd.read_excel(orders_file)
orders_coords_xl = pd.read_excel(clear_orders_file)
orders_all_xl = pd.concat([orders_lx, orders_coords_xl.reindex(orders_lx.index)], axis=1)
points_mapping = {(round(float(row['Широта']), 6), round(float(row['Долгота']), 6)): row['Адрес из Excel']
                  for _, row in orders_all_xl.iterrows()}

storages_file = './data/Склады.xlsx'
depots_xl = pd.read_excel(storages_file)
depots_mapping = {(round(float(row['Широта']), 6), round(float(row['Долгота']), 6)): row['Адрес']
                  for _, row in depots_xl.iterrows()}

points_mapping.update(depots_mapping)


def parse_shit(shit: str):
    with open(shit, 'r') as f:
        solutions = ujson.load(f)

    writer = pd.ExcelWriter('output.xlsx')

    shit = defaultdict(list)
    for j, solution in enumerate(solutions):

        if 'indexes' not in solution:
            answer = {'why': [solution['unassigned'][0]['reasons'][0]['description']]}
            pd.DataFrame.from_dict(answer).to_excel(writer, sheet_name=f'problem_{j}')
            continue

        mapping = solution['indexes']
        solution = solution['solution']
        for tour in solution['tours']:
            stops = defaultdict(list)
            for i, stop in enumerate(tour['stops']):
                if i == 0 or i == len(tour['stops']) - 1:
                    continue
                loc = mapping[str(stop['location']['index'])]
                loc = (round(loc['lat'], 6), round(loc['lon'], 6))
                stops['point'].append(points_mapping[loc] if loc in points_mapping else loc)
                stops['job'].append(stop['activities'][0]['type'])
                stops['arrival'].append(stop['time']['arrival'])
                stops['departure'].append(stop['time']['departure'])
            pd.DataFrame.from_dict(stops).to_excel(writer, sheet_name=f'{tour["vehicleId"][:31]}')

        loc = mapping[str(solution['tours'][0]['stops'][1]['location']['index'])]
        loc = (round(loc['lat'], 6), round(loc['lon'], 6))
        shit['point'].append(points_mapping[loc] if loc in points_mapping else loc)
        shit['distance'].append(solution['statistic']['distance'])
        shit['duration'].append(solution['statistic']['duration'])

    pd.DataFrame.from_dict(shit).to_excel(writer, sheet_name='all')
    writer.save()


parse_shit('answer.json')
