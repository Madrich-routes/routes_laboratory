from models.problems.base import BaseRoutingProblem
from models.rich_vrp.visit import Visit
from typing import List
from datetime import datetime


import pandas as pd

class VRPSolution:
    def __init__(
            self,
            problem: BaseRoutingProblem,
            routes: List[List[Visit]]
    ):
        # TODO: адекватно оформить решение
        self.problem = problem
        self.routes = routes
        # self.

    def to_excel(
        self,
        path: str
    ):
        with pd.ExcelWriter(path, datetime_format='DD.MM.YYYY HH:MM:SS') as writer:
            columns = ['ID','Местоположение','Загрузка','Время прибытия','Длительность доставки']
            i, row_index = 0, 0
            for route in self.routes:
                i+=1
                name = [f"Маршрут {i}"]
                name_df = pd.DataFrame(name)
                name_df.to_excel(writer, startrow=row_index , startcol=0, index=False, header=None)
                row_index += 1
                route_list = []
                for visit in route:
                    row = [visit.job.id, 
                            ' '.join([str(visit.job.lat), str(visit.job.lon)]),
                            ' '.join(str(x) for x in visit.job.amounts.tolist()),
                            datetime.fromtimestamp(visit.time),
                            visit.job.delay]
                    route_list.append(row)
                row_df = pd.DataFrame(route_list, columns=columns)
                row_df.to_excel(writer, startrow=row_index , startcol=0, index=False)
                row_index += len(route)+1
            print('done')
            


