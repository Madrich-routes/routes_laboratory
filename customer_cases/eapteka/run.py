import math
import os
from copy import deepcopy

import numpy as np
import pandas as pd

from customer_cases.eapteka.genetic_solver.eapteka import get_solution
from customer_cases.eapteka.genetic_solver.excel_work import save_excel, save_couriers, convert_excel
from customer_cases.eapteka.genetic_solver.parse_data import parse_data, load_matrix

array = np.ndarray

TYPE = 'transport_simple'
profiles = [TYPE, 'driver']


def run_pharmacy():
    orders_loc = pd.read_excel('./data/update_3.xlsx')
    address_mapping = {}
    for i, row in orders_loc.iterrows():
        lat, lng = row['lat'], row['lng']
        address_mapping[(lat, lng)] = (row['place'], row['was'], row['corrected'])

    num, aver = 0, 0
    orders_inf = pd.read_excel('./data/Заказы_13.xlsx')
    for i, row in orders_inf.iterrows():
        if not math.isnan(row['ВесЗаказа']) and not math.isnan(row['ОбъемЗаказа']):
            num += 1
            aver += (row['ВесЗаказа'] / row['ОбъемЗаказа'])
    aver = aver / num

    orders, depots, couriers, mapping = parse_data(TYPE, aver, address_mapping)
    global_revers = {v: k for k, v in mapping.items()}

    points, internal_mappings, files = load_matrix(profiles, depots, global_revers, orders, address_mapping)

    depots = {k: v for k, v in sorted(depots.items(), key=lambda x: x[1].time_window[0][11:13], reverse=True)}

    tmp_depots = [(i, k, v) for i, (k, v) in enumerate(depots.items())]
    tmp_depots[0], tmp_depots[9] = tmp_depots[9], tmp_depots[0]
    tmp_depots[1], tmp_depots[8] = tmp_depots[8], tmp_depots[1]
    tmp_depots[2], tmp_depots[3] = tmp_depots[3], tmp_depots[2]
    depots = {k: v for _, k, v in tmp_depots}

    couriers_file, depots_file, couriers_dir = 'couriers.csv', 'depots.csv', './couriers'
    if not os.path.exists(couriers_dir):
        os.mkdir(couriers_dir)

    get_solution(depots, deepcopy(couriers), orders, internal_mappings, files, profiles,
                 address_mapping, couriers_file, depots_file, couriers_dir)

    solver_info = save_excel('20', couriers_file, depots_file)
    save_couriers('20', couriers_dir)
    convert_excel(solver_info)


run_pharmacy()
