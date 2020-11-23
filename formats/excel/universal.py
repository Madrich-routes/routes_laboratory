from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

import settings
from models.rich_vrp import Agent, AgentType, AgentCosts, Job, Depot
from models.rich_vrp.geometries.geometry import DistanceMatrixGeometry
from models.rich_vrp.problem import RichVRPProblem


class StandardDataFormat:
    """
    Наш универсальный формат Excel-файлов под импорт для дальнейшей работы
    Внутри состоит из 3-х листов:
    1. Заказы:
        [Широта, Долгота, Адрес, Временные рамки, Характеристики, Время обслуживания, Цена, Приоритет]  !!! storage_id
        [lat: float, lon: float, address: string, time_windows: List[Tuple[int, int]],
         amounts: np.ndarray, delay: int, price: int, priority:int]
    2. Курьеры
        [Имя, График работы, Профиль, Начальная точка, Конечная точка]
        [name: str, time_windows: List[Tuple[int, int]], type: str, start_place: int, end_place: int]
    3. Склады
        [Адрес, Широта, Долгота, График работы, Время обслуживания]
        [address: str, lat: float, lon: float, time_windows: List[Tuple[int, int]], delay: int]
    4. Профили
        id - Название - type - средняя скорость
    """

    @staticmethod
    def generate_dataframes(jobs_list: list, agents_list: list, depots_list: list) -> tuple:
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

    @staticmethod
    def to_excel(problem: RichVRPProblem, path: str):
        """Конвертируем RichVRPProblem в наш Excel.

        Parameters
        ----------
        problem :RichVRPProblem,
        path: str

        Returns
        -------
        """
        jobs_list = [
            [
                job.lat,
                job.lon,
                '',
                time_windows_to_str(job.time_windows),
                ', '.join([str(i) for i in job.amounts]),
                job.delay,
                job.price,
                job.priority,
            ]
            for job in problem.jobs
        ]

        agents_list = [
            [
                agent.name,
                time_windows_to_str(agent.time_windows),
                agent.type.name,
                agent.start_place,
                agent.end_place,
            ]
            for agent in problem.agents
        ]

        depots_list = [
            [
                depot.name,
                depot.lat,
                depot.lon,
                time_windows_to_str(depot.time_windows),
                depot.delay,
            ]
            for depot in problem.depots
        ]

        jobs, agents, depots = StandardDataFormat.generate_dataframes(jobs_list, agents_list, depots_list)
        with pd.ExcelWriter(path, datetime_format='DD.MM.YYYY HH:MM:SS') as writer:
            jobs.to_excel(writer, sheet_name='Заказы')
            agents.to_excel(writer, sheet_name='Курьеры')
            depots.to_excel(writer, sheet_name='Склады')

    @staticmethod
    def from_excel(path: str) -> RichVRPProblem:
        """Конвертируем наш Excel в RichVRPProblem.

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
            if type(row['Характеристики']) == str:
                amounts = np.array([int(i) for i in row['Характеристики'].split(', ')])
            else:
                amounts = np.array(row['Характеристики'])
            job = Job(
                id=i,
                name='',
                lat=row['Широта'],
                lon=row['Долгота'],
                x=0,
                y=0,
                time_windows=str_to_time_windows(row['Временные рамки']),
                delay=row['Время обслуживания'],
                amounts=amounts,
                required_skills=set(),
                price=row['Цена'],
                priority=row['Приоритет'],
            )
            jobs_list.append(job)

        for i in range(len(agents.index)):
            row = agents.iloc[i]
            costs = AgentCosts()
            agent = Agent(
                id=i,
                costs=costs,
                amounts=[],
                time_windows=str_to_time_windows(row['График работы']),
                compatible_depots=set(),
                start_place=row['Начальная точка'],
                end_place=row['Конечная точка'],
                type=AgentType(0, [10, 20], [], 'driver', 'Петя'),
                name=row['Имя'],
            )
            agents_list.append(agent)

        for i in range(len(depots.index)):
            row = depots.iloc[i]
            depot = Depot(
                id=0,
                time_windows=str_to_time_windows(row['График работы']),
                lat=row['Широта'],
                lon=row['Долгота'],
                delay=row['Время обслуживания'],
                name=row['Адрес'],
            )
            depots_list.append(depot)
        return RichVRPProblem(
            DistanceMatrixGeometry(np.array([]), np.array([]), 0),
            agents_list,
            jobs_list,
            depots_list,
            [],
        )

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


if __name__ == '__main__':
    def main():
        start = int(datetime(2020, 11, 3, 8, 00).timestamp())
        end = int(datetime(2020, 11, 3, 20, 00).timestamp())
        costs = AgentCosts()
        depot = Depot(0, [(start, end)], 55.75, 37.61, 0, 'Адрес тут')
        agent = Agent(
            id=0,
            costs=costs,
            amounts=[10, 20],
            time_windows=[(start, end)],
            compatible_depots={depot},
            start_place=None,
            end_place=None,
            type=AgentType(0, [10, 20], [], 'driver', 'Петя'),
            name='Алексей',
        )
        job = Job(
            id=0,
            name='Доставка 1',
            lat=55.75,
            lon=37.61,
            x=0,
            y=0,
            delay=5,
            time_windows=[(start, end), (start, end)],
            amounts=np.array([10, 20]),
            required_skills={2},
            price=5,
            depots=[depot],
        )
        res = RichVRPProblem(
            DistanceMatrixGeometry(np.array([]), np.array([]), 0),
            [agent],
            [job],
            [depot],
            [],
        )

        test = StandardDataFormat()
        test.to_excel(res, settings.DATA_DIR / 'tests/tst.xlsx')
        test.from_excel(settings.DATA_DIR / 'tests/tst.xlsx')
        print('ok')


    main()
