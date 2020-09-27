import math
from copy import deepcopy

import numpy as np
import pandas as pd

from customer_cases.eapteka.genetic_solver.eapteka import parse_data, download_matrix, get_solution
from customer_cases.eapteka.genetic_solver.excel_work import save_excel, save_couriers, convert_excel

array = np.ndarray

HERE_KEY = 'hH0EHA4kmtfQFytyz0yDWeF0HYKvX0aDqKIGYXYoK0M'
TYPE = 'transport_simple'
profiles = [TYPE, 'driver']

orders_loc = pd.read_excel('./data/update_3.xlsx')

address_mapping = {}
address_before = {}
address_corrected = {}
for i, row in orders_loc.iterrows():
    lat, lng = row['lat'], row['lng']
    address_mapping[(lat, lng)] = row['place']
    address_before[(lat, lng)] = row['was']
    address_corrected[(lat, lng)] = row['corrected']

num, aver = 0, 0
orders_inf = pd.read_excel('./data/Заказы_13.xlsx')
for i, row in orders_inf.iterrows():
    if not math.isnan(row['ВесЗаказа']) and not math.isnan(row['ОбъемЗаказа']):
        num += 1
        aver += (row['ВесЗаказа'] / row['ОбъемЗаказа'])
aver = aver / num

orders, depots, couriers, mapping = parse_data(TYPE, aver, address_mapping, address_before, address_corrected)
global_revers = {v: k for k, v in mapping.items()}

points, internal_mappings, files = download_matrix(profiles, depots, global_revers, orders,
                                                   address_mapping, address_before, address_corrected)

depots = {k: v for k, v in sorted(depots.items(), key=lambda x: x[1].time_window[0][11:13], reverse=True)}

tmp_depots = [(i, k, v) for i, (k, v) in enumerate(depots.items())]
tmp_depots[0], tmp_depots[9] = tmp_depots[9], tmp_depots[0]
tmp_depots[1], tmp_depots[8] = tmp_depots[8], tmp_depots[1]
tmp_depots[2], tmp_depots[3] = tmp_depots[3], tmp_depots[2]
depots = {k: v for _, k, v in tmp_depots}

get_solution(depots, deepcopy(couriers), orders, internal_mappings, files, profiles,
             address_mapping, address_before, address_corrected)

save_excel(17, 'couriers.csv', 'depot.csv')
save_couriers(17, './couriers')
convert_excel('solver_17_info.xlsx')
