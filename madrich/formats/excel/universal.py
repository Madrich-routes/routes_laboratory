from datetime import datetime
from typing import List, Tuple

import pandas as pd
import json

from madrich.models.rich_vrp.agent import Agent
from madrich.models.rich_vrp.depot import Depot
from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.problem import RichVRPProblem


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
            [Широта, Долгота, Адрес, Временные рамки, Характеристики, Время обслуживания, Цена, Приоритет, Storage id]
            [lat: float, lon: float, name: string, time_windows: List[Tuple[int, int]],
             capacity_constraints: List[int], delay: int, price: int, priority:int, storage id: int]
        '''
        jobs = pd.DataFrame(jobs_list)
        jobs = jobs[
            ['lat', 'lon', 'name', 'time_windows', 'capacity_constraints', 'delay', 'price', 'priority', 'depot']]

        jobs['depot'] = jobs['depot'].apply(lambda x: x['name'])
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
            'Депо'
        ]

        # jobs.to_excel("output.xlsx")
        ####################################################
        '''
        2. Курьеры
            [Имя, График работы, Профиль, Вместимость, Посещаемые склады, Цена]
            [name: str, time_windows: List[Tuple[str, str]], profile: str, capacity_constraints: List[int],
            compatible_depots: List[int], costs_fixed: float, cost_distance: float, cost_time: float]
        '''
        agents = pd.DataFrame(agents_list)
        agents = agents[['name', 'time_windows', 'profile', 'capacity_constraints', 'compatible_depots', 'costs']]

        agents[['fixed', 'distance', 'time']] = pd.DataFrame(agents['costs'].to_list())
        agents['compatible_depots'] = agents['compatible_depots'].apply(lambda x: [i['name'] for i in x])
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
    def from_json(json_agents, json_jobs, json_depots, json_profiles) -> tuple:
        jobs_list, agents_list, depots_list, profiles_list = [], [], [], []

        agents = json.loads(json_agents)
        jobs = json.loads(json_jobs)
        depots = json.loads(json_depots)
        profiles = json.loads(json_profiles)

        depots_map = {}
        for i in range(len(depots)):
            row = depots[i]
            depot = Depot(
                id=0,
                time_window=str_to_time_windows(row['График работы'])[0],
                lat=row['Широта'],
                lon=row['Долгота'],
                delay=row['Время обслуживания'],
                name=row['Адрес'],
            )
            depots_list.append(depot)
            depots_map[row['Адрес']] = depot

        for i in range(len(jobs)):
            row = jobs[i]
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
                depot=depots_map[row['Депо']]
            )
            jobs_list.append(job)

        for i in range(len(agents)):
            row = agents[i]

            deps = eval(row['Посещаемые склады'])
            compatible_depots = [depots_map[i] for i in deps]
            agent = Agent(
                id=i,
                costs={'fixed': row['Фиксированная цена'],
                       'distance': row['Цена расстояния'],
                       'time': row['Цена время']},
                time_windows=str_to_time_windows(row['График работы']),
                compatible_depots=compatible_depots,
                name=row['Имя'],
                skills=[],
                profile=row['Профиль'],
                capacity_constraints=[int(i) for i in row['Вместимость'].strip("[]").split(',')]
            )
            agents_list.append(agent)

        for i in range(len(profiles)):
            row = profiles[i]
            profile = {row['Профиль']: (row['Тип'], row['Средняя скорость'])}
            profiles_list.append(profile)

        return agents_list, jobs_list, depots_list, profiles_list

    @staticmethod
    def from_excel_to_json(path: str) -> tuple:
        with pd.ExcelFile(path) as xls:
            jobs = pd.read_excel(xls, 'Заказы')
            agents = pd.read_excel(xls, 'Курьеры')
            depots = pd.read_excel(xls, 'Склады')
            profiles = pd.read_excel(xls, 'Профили')

        #######################################################################
        agents_j = []
        for i in range(len(agents.index)):
            row = agents.iloc[i]
            obj = {
                'Имя': row['Имя'],
                'График работы': row['График работы'],
                'Профиль': row['Профиль'],
                'Вместимость': row['Вместимость'],
                'Посещаемые склады': row['Посещаемые склады'],
                'Фиксированная цена': float(row['Фиксированная цена']),
                'Цена расстояния': float(row['Цена расстояния']),
                'Цена время': float(row['Цена время']),
            }
            agents_j.append(obj)

        json_agents = json.dumps(agents_j, ensure_ascii=False, )
        # print()
        # print(json_agents)
        #######################################################################
        jobs_j = []
        for i in range(len(jobs.index)):
            row = jobs.iloc[i]
            obj = {
                'Широта': row['Широта'],
                'Долгота': row['Долгота'],
                'Адрес': row['Адрес'],
                'Временные рамки': row['Временные рамки'],
                'Характеристики': row['Характеристики'],
                'Время обслуживания': int(row['Время обслуживания']),
                'Цена': int(row['Цена']),
                'Приоритет': int(row['Приоритет']),
                'Депо': row['Депо'],
            }
            jobs_j.append(obj)

        json_jobs = json.dumps(jobs_j, ensure_ascii=False, )
        # print()
        # print(json_jobs)
        #######################################################################
        depots_j = []
        for i in range(len(depots.index)):
            row = depots.iloc[i]
            obj = {
                'Адрес': row['Адрес'],
                'Широта': float(row['Широта']),
                'Долгота': float(row['Долгота']),
                'График работы': row['График работы'],
                'Время обслуживания': int(row['Время обслуживания']),
            }
            depots_j.append(obj)

        json_depots = json.dumps(depots_j, ensure_ascii=False, )
        # print()
        # print(json_depots)
        #######################################################################
        profiles_j = []
        for i in range(len(profiles.index)):
            row = profiles.iloc[i]
            obj = {
                'Профиль': row['Профиль'],
                'Тип': row['Тип'],
                'Средняя скорость': row['Средняя скорость'],
            }
            profiles_j.append(obj)

        json_profiles = json.dumps(profiles_j, ensure_ascii=False, )
        # print()
        # print(json_profiles)
        #######################################################################

        return json_agents, json_jobs, json_depots, json_profiles

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
            profiles = pd.read_excel(xls, 'Профили')

        jobs_list, agents_list, depots_list, profiles_list = [], [], [], []
        depots_map = {}
        for i in range(len(depots.index)):
            row = depots.iloc[i]
            depot = Depot(
                id=i,
                time_window=str_to_time_windows(row['График работы'])[0],
                lat=row['Широта'],
                lon=row['Долгота'],
                delay=row['Время обслуживания'],
                name=row['Адрес'],
            )
            depots_list.append(depot)
            depots_map[row['Адрес']] = depot

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
                depot=depots_map[row['Депо']]
            )
            jobs_list.append(job)

        for i in range(len(agents.index)):
            row = agents.iloc[i]

            deps = eval(row['Посещаемые склады'])
            compatible_depots = [depots_map[i] for i in deps]
            agent = Agent(
                id=i,
                costs={'fixed': row['Фиксированная цена'],
                       'distance': row['Цена расстояния'],
                       'time': row['Цена время']},
                time_windows=str_to_time_windows(row['График работы']),
                compatible_depots=compatible_depots,
                name=row['Имя'],
                skills=[],
                profile=row['Профиль'],
                capacity_constraints=[int(i) for i in row['Вместимость'].strip("[]").split(',')]
            )
            agents_list.append(agent)

        for i in range(len(profiles.index)):
            row = profiles.iloc[i]
            profile = {row['Профиль']: (row['Тип'], row['Средняя скорость'])}
            profiles_list.append(profile)

        return agents_list, jobs_list, depots_list, profiles_list


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


def test_sdf():
    from madrich.solvers.vrp_cli.generators import generate_mdvrp

    agents_list, jobs_list, depots_list = generate_mdvrp(15, 3, 5)

    StandardDataFormat.to_excel(agents_list, jobs_list, depots_list, 'output2.xlsx')
    a, j, d, p = StandardDataFormat.from_excel('output2.xlsx')

    j_a, j_j, j_d, j_p = StandardDataFormat.from_excel_to_json('output2.xlsx')

    a_, j_, d_, p_ = StandardDataFormat.from_json(j_a, j_j, j_d, j_p)

    print()
    print('Исходный           ', agents_list[0])
    print('to_exel + from_exel', a[0])
    print('from_exel_to_json  ', j_a)
    print('from_json          ', a_[0])

    print()
    print('Исходный           ', jobs_list[0])
    print('to_exel + from_exel', j[0])
    print('from_exel_to_json  ', j_j)
    print('from_json          ', j_[0])

    print()
    print('Исходный           ', depots_list[0])
    print('to_exel + from_exel', d[0])
    print('from_exel_to_json  ', j_d)
    print('from_json          ', d_[0])

    print()
    print('to_exel + from_exel', p[0])
    print('from_exel_to_json  ', j_p)
    print('from_json          ', p_[0])
