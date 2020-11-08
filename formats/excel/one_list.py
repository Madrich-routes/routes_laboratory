from datetime import datetime

import pandas as pd

from models.rich_vrp import VRPSolution


def to_excel(
        solution: VRPSolution,
        path: str
):
    """Сохраняем результат в excel на один лист.

    Parameters
    ----------
    solution :
    path :

    Returns
    -------
    """
    with pd.ExcelWriter(path, datetime_format='DD.MM.YYYY HH:MM:SS') as writer:
        columns = ['ID', 'Местоположение', 'Загрузка', 'Время прибытия', 'Длительность доставки']
        i, row_index = 0, 0

        for route in solution.routes:
            i += 1
            name = [f"Маршрут {i}"]
            name_df = pd.DataFrame(name)
            name_df.to_excel(writer, startrow=row_index, startcol=0, index=False, header=None)
            row_index += 1
            route_list = []
            for visit in route:
                row = [
                    visit.place.id,
                    ' '.join([str(visit.place.lat), str(visit.place.lon)]),
                    ' '.join(str(x) for x in visit.place.amounts.tolist()),
                    datetime.fromtimestamp(visit.time),
                    visit.place.delay
                ]
                route_list.append(row)
            row_df = pd.DataFrame(route_list, columns=columns)
            row_df.to_excel(writer, startrow=row_index, startcol=0, index=False)
            row_index += len(route) + 1
        print('done')
