from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

from madrich import settings
from madrich.models.rich_vrp.agent import Agent
from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.geometries.geometry import DistanceMatrixGeometry
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.problem import RichVRPProblem

from madrich.solvers.vrp_cli.generators import profiles


class StandardDataFormat:
    """
    Наш универсальный формат Excel-файлов под импорт для дальнейшей работы
    Время в RFC3339
    Внутри состоит из 4-х листов:
    1. Заказы:
        [Широта, Долгота, Адрес, Временные рамки, Характеристики, Время обслуживания, Цена, Приоритет, Storage id]
        [lat: float, lon: float, address: string, time_windows: List[Tuple[str, str]],
         amounts: List[int], delay: int, price: int, priority:int, storage id: int]
    2. Курьеры
        [Имя, График работы, Профиль, Начальная точка, Конечная точка, Посещаемые склады]
        [name: str, time_windows: List[Tuple[str, str]], capacity: List[int], profile: str, depots: List[int]]
    3. Склады
        [Индификатор, Адрес, Широта, Долгота, График работы, Время обслуживания]
        [storage id: int, address: str, lat: float, lon: float, time_windows: List[Tuple[str, str]], delay: int]
    4. Профили
        Название - type - средняя скорость
    """

    @staticmethod
    def generate_dataframes(agents_list: list, jobs_list: list, depots_list: list) -> tuple:
        """Генерация фреймов для экселек

        Parameters
        ----------
        jobs_list: list
        agents_list: list
        depots_list: list

        Returns
        -------
        Фреймы: задачи, агенты, демо
        """

        ####################################################
        '''
        1. Заказы:
            [Широта, Долгота, Адрес, Временные рамки, Характеристики, Время обслуживания, Цена, Приоритет]  !!! storage_id
            [lat: float, lon: float, name: string, time_windows: List[Tuple[int, int]],
             capacity_constraints: List[int], delay: int, price: int, priority:int]
        '''
        jobs = pd.DataFrame(jobs_list)
        jobs = jobs[['lat', 'lon', 'name', 'time_windows', 'capacity_constraints', 'delay', 'price', 'priority']]

        jobs['time_windows'] = jobs['time_windows'].apply(time_windows_to_str)
        jobs['capacity_constraints'] = jobs['capacity_constraints'].apply(lambda x: ' '.join([str(el) for el in x]))
        jobs.columns = [
            'Широта',
            'Долгота',
            'Адрес',
            'Временные рамки',
            'Характеристики',
            'Время обслуживания',
            'Цена',
            'Приоритет',
        ]

        # jobs.to_excel("output.xlsx")
        ####################################################
        '''
        2. Курьеры
            [Имя, График работы, Профиль, Вместимость, Посещаемые склады, Цена]
            [name: str, time_windows: List[Tuple[str, str]], profile: str, capacity_constraints: List[int], compatible_depots: List[int]]
        '''
        agents = pd.DataFrame(agents_list)
        agents = agents[['name', 'time_windows', 'profile', 'capacity_constraints', 'compatible_depots', 'costs']]


        agents[['fixed', 'distance', 'time']] = pd.DataFrame(agents['costs'].to_list())

        del agents['costs']

        agents['time_windows'] = agents['time_windows'].apply(time_windows_to_str)
        agents.columns = [
            'Имя',
            'График работы',
            'Профиль',
            'Вместимость',
            'Посещаемые склады',
            'Фиксированная цена',
            'Цена расстояния',
            'Цена время',
        ]
        # agents.to_excel("output.xlsx")
        ####################################################
        '''
        3. Склады
            [Адрес, Широта, Долгота, График работы, Время обслуживания]
            [address: str, lat: float, lon: float, time_windows: List[Tuple[int, int]], delay: int]
        '''
        depots = pd.DataFrame(depots_list)
        depots = depots[['name', 'lat', 'lon', 'time_windows', 'delay']]

        depots['time_windows'] = depots['time_windows'].apply(time_windows_to_str)

        depots.columns = [
            'Адрес',
            'Широта',
            'Долгота',
            'График работы',
            'Время обслуживания',
        ]

        # depots.to_excel("output.xlsx")
        ####################################################
        '''
        4. Профили
            Название - type - средняя скорость
        '''
        profs = agents['Профиль'].to_list()
        profiles_df = pd.DataFrame(profs)
        profiles_df[['profile']] = profiles_df[0]
        profiles_df[['some']] = ""

        profiles_df.columns = [
            'Профиль',
            'Тип',
            'Средняя скорость'
        ]
        # profiles_df.to_excel("output.xlsx")
        ####################################################
        return jobs, agents, depots, profiles_df

    @staticmethod
    def to_excel(agents_list: list, jobs_list: list, depots_list: list, path: str):
        """Конвертируем RichVRPProblem в наш Excel.

        Parameters
        ----------
        jobs_list: list,
        agents_list: list,
        depots_list: list,
        path: str

        Returns
        -------
        """
        jobs, agents, depots, profiles_df = StandardDataFormat.generate_dataframes(agents_list, jobs_list, depots_list)
        with pd.ExcelWriter(path, datetime_format='DD.MM.YYYY HH:MM:SS') as writer:
            jobs.to_excel(writer, sheet_name='Заказы')
            agents.to_excel(writer, sheet_name='Курьеры')
            depots.to_excel(writer, sheet_name='Склады')
            profiles_df.to_excel(writer, sheet_name='Профили')

    @staticmethod
    def from_excel(path: str) -> tuple:
        """Конвертируем наш Excel в модели.

        Parameters
        ----------
        path: str

        Returns
        -------
        res:RichVRPProblem
        """
        with pd.ExcelFile(path) as xls:
            jobs = pd.read_excel(xls, 'Заказы')
            agents = pd.read_excel(xls, 'Курьеры')
            depots = pd.read_excel(xls, 'Склады')

        jobs_list, agents_list, depots_list = [], [], []

        jobs['Цена'].replace(r'', 0)
        jobs['Приоритет'].replace(r'', 0)

        for i in range(len(jobs.index)):
            row = jobs.iloc[i]
            job = Job(
                id=i,
                name=row['Адрес'],
                lat=row['Широта'],
                lon=row['Долгота'],
                x=None,
                y=None,
                time_windows=str_to_time_windows(row['Временные рамки']),
                delay=row['Время обслуживания'],
                capacity_constraints=[int(i) for i in row['Характеристики'].split()],
                required_skills=[],
                price=row['Цена'],
                priority=row['Приоритет'],
            )
            jobs_list.append(job)
        for i in range(len(agents.index)):
            row = agents.iloc[i]

            compatible_depots = []
            deps = eval(row['Посещаемые склады'])
            for d in deps:
                compatible_depots.append(Depot(
                    id=d['id'],
                    name=d['name'],
                    lat=d['lat'],
                    lon=d['lon'],
                    delay=d['delay'],
                    time_window=d['time_windows'],
                ))
            agent = Agent(
                id=i,
                costs={'fixed': row['Фиксированная цена'], 'distance': row['Цена расстояния'], 'time': row['Цена время']},
                time_windows=str_to_time_windows(row['График работы']),
                compatible_depots=compatible_depots,
                name=row['Имя'],
                skills=[],
                profile=row['Профиль'],
                capacity_constraints=[int(i) for i in row['Вместимость'].strip("[]").split(',')]
            )
            agents_list.append(agent)

        for i in range(len(depots.index)):
            row = depots.iloc[i]
            depot = Depot(
                id=0,
                time_window=str_to_time_windows(row['График работы'])[0],
                lat=row['Широта'],
                lon=row['Долгота'],
                delay=row['Время обслуживания'],
                name=row['Адрес'],
            )
            depots_list.append(depot)
        return agents_list, jobs_list, depots_list

    @staticmethod
    def generate_random(jobs: int, storages: int, couriers: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Генерируем рандомную задачу
        Parameters
        ----------
        jobs: int, (всего будет задач jobs * storages)
        storages: int,
        couriers: int

        Returns
        -------
        3 фрейма с Заказами, Курьерами, Складами
        """
        jobs_list = []

        agents_list = []

        depots_list = []

        jobs = pd.DataFrame(
            jobs_list,
            columns=[
                'Широта',
                'Долгота',
                'Адрес',
                'Временные рамки',
                'Характеристики',
                'Время обслуживания',
                'Цена',
                'Приоритет',
            ],
        )

        agents = pd.DataFrame(
            agents_list,
            columns=[
                'Имя',
                'График работы',
                'Тип',
                'Начальная точка',
                'Конечная точка',
            ],
        )

        depots = pd.DataFrame(
            depots_list,
            columns=[
                'Адрес',
                'Широта',
                'Долгота',
                'График работы',
                'Время обслуживания',
            ],
        )

        return jobs, agents, depots


def time_windows_to_str(time_windows: List[Tuple[int, int]]) -> str:
    """Приведение стандартного time_windows в удобочитаемый вид.

    Parameters
    ----------
    time_windows: List[Tuple[int, int]]

    Returns
    -------
    str
    """
    return ', '.join(
        [
            f'({datetime.fromtimestamp(i[0])} - {datetime.fromtimestamp(i[1])})'
            for i in time_windows
        ]
    )


def str_to_time_windows(raw_string: str) -> List[Tuple[int, int]]:
    """Приведение временных рамок в time_windows.

    Parameters
    ----------
    raw_string: str

    Returns
    -------
    List[Tuple[int, int]]
    """
    sep_strings = raw_string.split(', ')

    return [
        (
            int(
                datetime.strptime(
                    item[1:-2].split(' - ')[0], '%Y-%m-%d %H:%M:%S'
                ).timestamp()
            ),
            int(
                datetime.strptime(
                    item[1:-2].split(' - ')[1], '%Y-%m-%d %H:%M:%S'
                ).timestamp()
            ),
        )
        for item in sep_strings
    ]

# if __name__ == '__main__':
#     def main():
#         start = int(datetime(2020, 11, 3, 8, 00).timestamp())
#         end = int(datetime(2020, 11, 3, 20, 00).timestamp())
#         costs = AgentCosts()
#         depot = Depot(0, [(start, end)], 55.75, 37.61, 0, 'Адрес тут')
#         agent = Agent(
#             id=0,
#             costs=costs,
#             amounts=[10, 20],
#             time_windows=[(start, end)],
#             compatible_depots={depot},
#             start_place=None,
#             end_place=None,
#             type=AgentType(0, [10, 20], [], 'driver', 'Петя'),
#             name='Алексей',
#         )
#         job = Job(
#             id=0,
#             name='Доставка 1',
#             lat=55.75,
#             lon=37.61,
#             x=0,
#             y=0,
#             delay=5,
#             time_windows=[(start, end), (start, end)],
#             amounts=np.array([10, 20]),
#             required_skills={2},
#             price=5,
#             depots=[depot],
#         )
#         res = RichVRPProblem(
#             DistanceMatrixGeometry(np.array([]), np.array([]), 0),
#             [agent],
#             [job],
#             [depot],
#             [],
#         )
#
#         test = StandardDataFormat()
#         test.to_excel(res, settings.DATA_DIR / 'tests/tst.xlsx')
#         test.from_excel(settings.DATA_DIR / 'tests/tst.xlsx')
#         print('ok')
#
#
#     main()
