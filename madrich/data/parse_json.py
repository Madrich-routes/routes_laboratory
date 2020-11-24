from datetime import datetime

import pandas as pd
import ujson

xl = pd.ExcelFile('24_couriers.xlsx')
names = xl.sheet_names

output = []

for i, name in enumerate(names):
    data = pd.read_excel('24_couriers.xlsx', sheet_name=name)
    d = []
    for j, row in data.iterrows():
        loc = row['loc'].replace(',', '').replace('(', '').replace(')', '').split(' ')
        d.append({
            'coordinates': [float(loc[0]), float(loc[1])],
            'time_entry': int(datetime.strptime(row['arrival'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
            'time_exit': int(datetime.strptime(row['departure'], '%Y-%m-%dT%H:%M:%SZ').timestamp())
        })
    output.append(d)

with open('24_tour.json', 'w') as f:
    ujson.dump(output, f)
