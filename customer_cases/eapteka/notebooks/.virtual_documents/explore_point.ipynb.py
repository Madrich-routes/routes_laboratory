import pandas as pd
import numpy as np
import lightgbm as lgb
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import missingno as msno
from lightgbm import LGBMRegressor
from numba import jit

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="get_ipython().run_line_magic("(message)s",", "")
    datefmt="[get_ipython().run_line_magic("X]",", "")
    handlers=[RichHandler(rich_tracebacks=True)]
)

from rich.traceback import install
install()

# всякие магиеческие метды
get_ipython().run_line_magic("load_ext", " autoreload")
get_ipython().run_line_magic("autoreload", " 2")

get_ipython().run_line_magic("matplotlib", " inline")

get_ipython().run_line_magic("env", " OMP_NUM_THREADS=72")
get_ipython().run_line_magic("config", " InlineBackend.figure_format ='retina'")

pd.set_option('display.max_rows', 30)
pd.options.display.max_columns = None
pd.options.display.float_format = '{:,.3f}'.format

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


coords = pd.read_excel("../data/update_3.xlsx")
info = pd.read_excel("../data/Заказы_13.xlsx")
stocks = pd.read_excel("../data/Склады.xlsx")
data = coords.join(info)

prior_points = data[~data['Приоритет'].isna()]


stocks['lat'] = stocks['Широта']
stocks['lng'] = stocks['Долгота']

stocks.head(2)
data.head(2)


import re

regex = r'Доставка с ([0-9]{0,2}).* по ([0-9]{0,2}).*$'

times = data['ИнтервалДоставки']
t_from = times.map(lambda x: re.search(regex, x).group(1))
t_to = times.map(lambda x: re.search(regex, x).group(2))

t_from.unique()
t_to.unique()


times[t_to == '']
times[t_from == '']


# фиксим отсутствующие
t_to[t_to == ''] = '24'
t_from[t_from == ''] = '00'

# фиксим типы данных
t_to = t_to.astype(int)
t_from = t_from.astype(int)

# фиксим нерабочие окна
t_to[t_to <= t_from] = 24

t_diffs = (t_to - t_from)
# График каждого количества
sns.histplot(t_diffs, bins=range(25), discrete=True)
# t_diffs.value_counts().head(30).plot(kind='barh', figsize=(20,10))
plt.xlabel('Количество временных окон каждого типав')
plt.show()

sns.histplot(t_from, discrete=True)
plt.xlabel('Начало временного окна')
plt.show()


sns.histplot(t_to, discrete=True)
plt.xlabel('Конец временного окна')
plt.show()


data['t_from'] = t_from
data['t_to'] = t_to
data['window_len'] = t_diffs


import seaborn as sns
import matplotlib.pyplot as plt

box = (36, 39.25, 55, 56.5)
fig, ax = plt.subplots(figsize=(20, 20))
sns.scatterplot(data=data, x='lng', y='lat', hue='t_from', ax=ax, palette='husl', s=15)
prior=data[~data['Приоритет'].isna()]

plt.scatter(x=prior.lng, y=prior.lat, c='r', s=40)
plt.scatter(y=stocks['Широта'].astype(float), x=stocks['Долгота'].astype('float'), c='b', marker='x', s=40)

plt.xlim(box[0], box[1])
plt.ylim(box[2], box[3])

map_back = plt.imread('../data/map.png')
ax.imshow(map_back, zorder=0, extent=box)


t


## Теперь через follium
import folium
import math
tiles='Stamen Toner'  # черно-белая
tiles = 'Stamen Terrain'  # растительность

mos_map = folium.Map(location=[55.7539, 37.6208], zoom_start=11, tiles=tiles)

unused = folium.map.FeatureGroup()
for t in data.loc[:, ('lat', 'lng', 'Приоритет', 't_from', 't_to')].itertuples():
#     print(t[3])
    if not math.isfinite(t[3]):
        color='yellow'
        fill_color='blue'
        radius=5
    else:
        color='red'
        fill_color='red'
        radius=10

    a = folium.CircleMarker(
        [t.lat, t.lng],
        radius=radius,
        color=color,
        popup=str(t),
        fill=False,
        fill_color=fill_color,
        fill_opacity=0.6,
    ).add_to(unused)

for t in stocks.itertuples():
    a = folium.Marker(
        [t.lat, t.lng],
    ).add_to(unused)
    
    
# folium.

mos_map.add_child(unused)






