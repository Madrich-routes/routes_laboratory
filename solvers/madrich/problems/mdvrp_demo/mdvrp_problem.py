import logging
from typing import Optional, List, Dict, Union, Tuple

import numpy as np

from madrich.problems.mdvrp_demo.models import Storage, Tour, Courier, Route, Job, Track, Problem
from madrich.problems.models import Matrix, State

array = np.ndarray


class ProblemMdvrp(Problem):

    @staticmethod
    def init(vec: int, storages: List[Storage], couriers: List[Courier], matrices: Dict[str, Matrix]) -> Tour:
        """ Строим жадно тур: по ближайшим подходящим соседям для каждого курьера
        :param vec: длина вектора value
        :param storages: все склады
        :param couriers: все доступные курьеры
        :param matrices: матрицы расстояний
        :return: тур
        """
        logging.info(f'\nCreating Tour: {[st.name for st in storages]}, Couriers: {len(couriers)}')
        tour = Tour(storages)

        for courier in couriers:  # строим маршрут для каждого курьера
            route = ProblemMdvrp.__greedy_route(vec, courier, matrices)
            tour.routes.append(route)

        logging.info(f'Created Tour, jobs: {sum([len(storage.assigned_jobs) for storage in storages])}')
        return tour

    @staticmethod
    def get_state(route: Route) -> Optional[State]:
        """ Подсчитываем праметры тура и проверяем на правильность и обновляем Route
        :param route: маршрут
        :return: состояние
        """
        size_t = len(route.tracks)
        if size_t == 0:
            return State.empty()
        location = route.courier.start_location.matrix_id
        state = State.empty()

        for track in route.tracks:
            state.value = np.zeros(route.vec, dtype=np.int64)
            # 1. Подходит ли он складу вообще
            if not ProblemMdvrp.__validate_skills(track.storage, route.courier):
                return None
            # 2. Едем на склад
            answer = ProblemMdvrp.__go_storage(location, state, track.storage, route)
            if answer is None:
                return None
            state += answer
            location = track.storage.location.matrix_id
            # 3. Проверяем каждую точку
            for job in track.jobs:
                if not ProblemMdvrp.__validate_skills(job, route.courier):
                    return None
                if not ProblemMdvrp.__validate_courier(state, route):
                    return None
                answer = ProblemMdvrp.__go_job(location, state, job, track.storage, route)
                if answer is None or not ProblemMdvrp.__validate_courier(answer, route):
                    return None
                location = job.location.matrix_id
                state += answer

        state += ProblemMdvrp.__end(location, route)
        if not ProblemMdvrp.__validate_courier(state, route):
            return None

        state.value = None
        return state

    @staticmethod
    def get_state_track(track: Track, route: Route) -> Optional[State]:
        """ Оценка снизу подмаршрута
        :param track: подмаршрут
        :param route: маршрут
        :return: оценка
        """
        location = track.storage.location.matrix_id
        state = State.empty()

        for job in track.jobs:
            tt = route.matrix.travel_time[location][job.location.matrix_id]
            d = route.matrix.distance[location][job.location.matrix_id]
            c = ProblemMdvrp.__cost(tt, d, route)
            location = job.location.matrix_id
            state += State(tt, d, c, job.value)

        return state

    @staticmethod
    def __greedy_route(vec: int, courier: Courier, matrices: Dict[str, Matrix]) -> Route:
        """ Строим жадно тур: по ближайшим подходящим соседям
        :param vec: длина вектора value
        :param courier: курьер для которого строим тур
        :param matrices: матрица расстояний/времени
        :return: новый маршрут
        """
        logging.info(f'Creating Route, Courier: {courier.name}, type: {courier.profile}')
        start_shift, _ = courier.work_time.window
        route = Route(courier, matrices[courier.profile], start_shift, vec=vec)
        state = State.empty()
        curr_location = courier.start_location.matrix_id

        while True:
            # 1. Инициализируем подмаршрут с одной точкой
            state.value = np.zeros(route.vec, dtype=np.int64)
            tmp = ProblemMdvrp.__init_track(curr_location, state, route)
            if tmp is None:
                break
            state, track = tmp
            curr_location = track.jobs[0].location.matrix_id

            while True:
                # 2. Добавляем по точке
                new_state = ProblemMdvrp.__choose_job(curr_location, state, track, route)
                if new_state is None:
                    break
                state = new_state
                curr_location = track.jobs[-1].location.matrix_id

            route.tracks.append(track)

        state += ProblemMdvrp.__end(curr_location, route)
        route.state += state
        logging.info(f'Route created, jobs: {sum([len(track.jobs) for track in route.tracks])}')
        return route

    @staticmethod
    def __end(curr_point: int, route: Route) -> State:
        """ Заканчиваем, едем с последней задачи в конечную точку
        :param curr_point: текущая позиция
        :param route: маршрут
        :return: состояние
        """
        distance_matrix = route.matrix.distance
        travel_time_matrix = route.matrix.travel_time
        end_id = route.courier.start_location.matrix_id
        tt = travel_time_matrix[curr_point][end_id]
        d = distance_matrix[curr_point][end_id]
        return State(tt, d, ProblemMdvrp.__cost(tt, d, route), None)

    @staticmethod
    def __cost(travel_time: int, distance: int, route: Route) -> float:
        """ Получение стоимости
        :param travel_time: изменение времени
        :param distance: изменение расстояния
        :param route: маршрут
        :return: увеличение стоимости
        """
        return travel_time * route.courier.cost.second + distance * route.courier.cost.meter

    @staticmethod
    def __validate_skills(obj: Union[Job, Storage], courier: Courier) -> bool:
        """ Проверяем, что задача или склад подходит курьеру
        :param obj: объект в котором проверяем умения
        :param courier: курьер с умениями
        :return: может или нет
        """
        for skill in obj.skills:
            if skill not in courier.skills:
                return False
        return True

    @staticmethod
    def __validate_courier(state: State, route: Route) -> bool:
        """ Проверяем, что курьер еще жив
        :param state: текущее состояние тура полностью
        :param route: маршрут
        :return: все норм или нет
        """
        # 1. проверяем время работы
        start_shift, end_shift = route.courier.work_time.window
        start_time = route.start_time
        if not (start_shift <= start_time + state.travel_time <= end_shift):
            return False
        # 2. проверяем максимальную дистанцию
        if state.distance > route.courier.max_distance:
            return False
        # 3. проверяем на перевес
        size_v = len(state.value)
        for i in range(size_v):
            if state.value[i] > route.courier.value[i]:
                return False
        return True

    @staticmethod
    def __validate_storage(travel_time: int, storage: Storage, route: Route) -> bool:
        """ Проверяем, что поездка на склад возможна
        :param travel_time: текущее время с начала работы маршрута
        :param storage: склад
        :param route: маршрут
        :return: может или нет
        """
        start_shift, end_shift = storage.work_time.window
        start_time = route.start_time
        if not (start_shift <= start_time + travel_time <= end_shift):
            return False
        return True

    @staticmethod
    def __validate_job(travel_time: int, job: Job, route: Route) -> bool:
        """ Проверяем, что поездка на эту задачу возможна
        :param travel_time: текущее время с начала работы маршрута
        :param job: заказ
        :param route: маршрут
        :return: может или нет
        """
        start_time = route.start_time
        for window in job.time_windows:
            start_shift, end_shift = window.window
            if start_shift <= start_time + travel_time <= end_shift:
                return True
        return False

    @staticmethod
    def __storages(location: int, state: State, route: Route) -> Optional[List[Storage]]:
        """ Выдает склады в порядке увеличения дальности поездки к нему
        :param location: текущая позиция
        :param state: текущее состояние тура
        :param route: маршрут
        :return: список доступных складов для поездки курьеров в порядке возрастания дальности
        """
        matrix = route.matrix
        states: List[Tuple[int, int]] = []  # время/индекс склада

        for i, storage in enumerate(route.courier.storages):  # только по складам, доступным курьеру
            # 1. Склад непустой
            if len(storage.unassigned_jobs) == 0:
                continue
            # 2. Курьер подходит
            if not ProblemMdvrp.__validate_skills(storage, route.courier):
                continue
            tt = matrix.travel_time[location][storage.location.matrix_id]
            d = matrix.distance[location][storage.location.matrix_id]
            new_state = State(tt, d, ProblemMdvrp.__cost(tt, d, route))
            tmp_state = state + new_state
            # 3. Доедет
            if not ProblemMdvrp.__validate_courier(tmp_state, route):
                continue
            if not ProblemMdvrp.__validate_storage(tmp_state.travel_time, storage, route):
                continue
            states.append((tt, i))

        if not states:
            return None
        states = sorted(states)
        s_storages = [route.courier.storages[0]] * len(states)
        # 4. Сортируем
        for i, state in enumerate(states):
            s_storages[i] = route.courier.storages[state[1]]
        return s_storages

    @staticmethod
    def __init_track(location: int, state: State, route: Route) -> Optional[Tuple[State, Track]]:
        """ Доехать до ближайщего непустого склада + создать подмаршрут
        :param location: текущая позиция
        :param state: текущее состояния полное
        :param route: маршрут
        :return: Новый подмаршрут
        """
        curr_storages = ProblemMdvrp.__storages(location, state, route)
        if curr_storages is None:
            return None

        for storage in curr_storages:
            # 1. Едем на склад
            tmp_state = ProblemMdvrp.__go_storage(location, state, storage, route)
            track = Track(storage)
            # 2. Пытаемся доехать хоть куда-то
            tmp_state = ProblemMdvrp.__choose_job(storage.location.matrix_id, state + tmp_state, track, route)
            if tmp_state is not None:
                return tmp_state, track

        return None

    @staticmethod
    def __choose_job(curr_point: int, state: State, track: Track, route: Route) -> Optional[State]:
        """ Получаем оценку стоимости поезки на следующую задачу; job will be added into Track
        :param curr_point: текущая позиция
        :param state: текущее полное состояние
        :param track: текущий подмаршрут
        :param route: маршрут
        :return: новое состояние тура
        """
        best_state: Optional[State] = None
        index = -1

        for i, job in enumerate(track.storage.unassigned_jobs):
            # 0. Ищем лучший валидный
            tmp_state = ProblemMdvrp.__go_job(curr_point, state, job, track.storage, route)
            if tmp_state is None:
                continue
            tmp_state += state
            # 1. Из него мы должны успеть вернуться
            end = ProblemMdvrp.__end(job.location.matrix_id, route)
            if not ProblemMdvrp.__validate_courier(tmp_state + end, route):
                continue
            # 2. Выбираем лучший
            if best_state is None or tmp_state < best_state:
                best_state, index = tmp_state, i

        if index == -1:
            return None
        job = track.storage.unassigned_jobs.pop(index)
        track.storage.assigned_jobs.append(job)
        track.jobs.append(job)
        return best_state

    @staticmethod
    def __go_storage(curr_point: int, state: State, storage: Storage, route: Route) -> Optional[State]:
        """ Оценка стоимости поездки на склад
        :param curr_point: текущая позиция
        :param state: полное состояние тура
        :param storage: склад
        :param route: маршрут
        :return: на сколько увеличится State
        """
        tt = route.matrix.travel_time[curr_point][storage.location.matrix_id] + storage.load
        d = route.matrix.distance[curr_point][storage.location.matrix_id]
        if not ProblemMdvrp.__validate_storage(state.travel_time + tt, storage, route):
            return None
        return State(tt, d, ProblemMdvrp.__cost(tt, d, route), None)

    @staticmethod
    def __go_job(curr_point: int, state: State, job: Job, storage: Storage, route: Route) -> Optional[State]:
        """ Оценка стоимости поездки на следующую задачу
        :param curr_point: текущая позиция
        :param state: полное состояние
        :param job: заказ
        :param storage: склад
        :param route: маршрут
        :return: на сколько увеличится State
        """
        tt = route.matrix.travel_time[curr_point][job.location.matrix_id] + job.delay
        d = route.matrix.distance[storage.location.matrix_id][job.location.matrix_id]
        if not ProblemMdvrp.__validate_job(state.travel_time + tt, job, route):
            return None
        tmp = State(tt, d, ProblemMdvrp.__cost(tt, d, route), job.value.copy())
        if not ProblemMdvrp.__validate_courier(tmp + state, route):
            return None
        return tmp
