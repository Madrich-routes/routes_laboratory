import logging
from copy import deepcopy
from typing import Dict, List, Optional, Union

import numpy as np

from solvers.madrich.problems.models import Matrix, State
from solvers.madrich.problems.vrp_demo.models import Courier, Job, Problem, Route, Storage, Tour

array = np.ndarray


class ProblemVrp(Problem):

    @staticmethod
    def init(storage: Storage, jobs: List[Job], couriers: List[Courier], matrices: Dict[str, Matrix]) -> Tour:
        return ProblemVrp.__greedy_tour(storage, jobs, couriers, matrices)

    @staticmethod
    def get_state(route: Route) -> Optional[State]:
        size_t = len(route.jobs)
        if size_t == 0:
            return State(0, 0, 0.)

        curr_point = route.storage.location.matrix_id
        state = ProblemVrp.__start(route)
        state.value = np.zeros(len(route.jobs[0].value), dtype=np.int64)

        for job in route.jobs:
            if not ProblemVrp.__validate_skills(job, route.courier):
                return None

            if not ProblemVrp.__validate_courier(state, route):
                return None

            answer = ProblemVrp.__next_job(curr_point, state, job, route)
            if answer is None or not ProblemVrp.__validate_courier(answer, route):
                return None

            state = answer
            curr_point = job.location.matrix_id

        state += ProblemVrp.__end(curr_point, route)
        if not ProblemVrp.__validate_courier(state, route):
            return None

        route.travel_time = state.travel_time
        route.distance = state.distance
        route.cost = state.cost

        state.value = None
        return state

    @staticmethod
    def __greedy_tour(storage: Storage, jobs: List[Job], couriers: List[Courier], matrices: Dict[str, Matrix]):
        """Строим жадно тур: по ближайшим подходящим соседям для каждого курьера."""
        logging.info(f'\nCreating Tour: {storage.name}, Couriers: {len(couriers)}, Jobs: {len(jobs)}')
        tour = Tour(storage, [], [])
        used_couriers = []

        for courier in couriers:
            if not ProblemVrp.__validate_skills(storage, courier):
                continue

            ret = [job for job in jobs if ProblemVrp.__validate_skills(job, courier)]
            route = ProblemVrp.__greedy_route(storage, ret, courier, matrices)
            if len(route) == 0:
                continue

            used_couriers.append(courier)
            for job in route.jobs:
                jobs.remove(job)
            tour.routes.append(route)

        for courier in used_couriers:
            couriers.remove(courier)

        tour.unassigned_jobs = jobs
        logging.info(f'Created Tour, Routes: {len(tour)}, Assigned: {tour.len_jobs() - len(jobs)}/{tour.len_jobs()}')
        return tour

    @staticmethod
    def __greedy_route(storage: Storage, jobs: List[Job], courier: Courier, matrices: Dict[str, Matrix]) -> Route:
        """Строим жадно тур: по ближайшим подходящим соседям."""
        logging.info(f'Creating Route, Courier: {courier.name}, jobs: {len(jobs)}, type: {courier.profile}')
        assert len(jobs) > 0, 'jobs error'
        matrix = matrices[courier.profile]
        start_shift, end_shift = courier.work_time.window
        route = Route(storage, courier, matrix, start_shift, [], 0, 0, 0.)

        curr_point = route.storage.location.matrix_id
        state = ProblemVrp.__start(route)
        state.value = np.zeros(len(jobs[0].value), dtype=np.int64)

        length, k = len(jobs), 0
        visited = set()

        while k < length - 1:
            best_job: Optional[Job] = None
            best_state: Optional[State] = None
            for job in jobs:
                if job.job_id in visited:
                    continue

                answer = ProblemVrp.__next_job(curr_point, state, job, route)
                if answer is None:
                    continue

                end = ProblemVrp.__end(job.location.matrix_id, route)
                if end is None or not ProblemVrp.__validate_courier(answer + end, route):
                    continue

                if best_job is None or answer < best_state:
                    best_job, best_state = job, answer

            if best_job is None:
                break

            state = best_state
            curr_point = best_job.location.matrix_id
            visited.add(best_job.job_id)
            route.jobs.append(best_job)
            k += 1

        state += ProblemVrp.__end(curr_point, route)
        route.save_state(state)
        logging.info(f'Created Route, Jobs: {len(route)}')
        return route

    @staticmethod
    def __validate_skills(obj: Union[Job, Storage], courier: Courier) -> bool:
        """Проверяем, что задача или склад подходит курьеру."""
        for skill in obj.skills:
            if skill not in courier.skills:
                return False
        return True

    @staticmethod
    def __next_job(curr_point: int, state: State, job: Job, route: Route) -> Optional[State]:
        """Получаем оценку стоимости поезкки на следующую задачу (со складом)"""
        state = deepcopy(state)
        answer = ProblemVrp.__go_job(curr_point, state, job, route)

        if answer is None:
            # 1. если не влезло едем на склад, если склад открыт и успеваем загрузиться до закрытия
            answer = ProblemVrp.__go_storage(curr_point, state, route)
            if answer is None:
                return None

            state += answer
            state.value = np.zeros(len(job.value), dtype=np.int64)

            # 2. едем на точку и успеваем отдать до конца окна
            answer = ProblemVrp.__go_job(route.storage.location.matrix_id, state, job, route)
            if answer is None:
                return None

            state += answer

        else:
            state += answer

        if state is None:
            return None

        return state

    @staticmethod
    def __cost(travel_time: int, distance: int, route: Route) -> float:
        """Получение стоимости."""
        return travel_time * route.courier.cost.second + distance * route.courier.cost.meter

    @staticmethod
    def __go_storage(curr_point: int, state: State, route: Route) -> Optional[State]:
        """Оценка стоимости поездки на склад."""
        tt = route.matrix.travel_time[curr_point][route.storage.location.matrix_id] + route.storage.load
        d = route.matrix.distance[curr_point][route.storage.location.matrix_id]

        if not ProblemVrp.__validate_storage(state.travel_time + tt, route):
            return None

        return State(tt, d, ProblemVrp.__cost(tt, d, route), None)

    @staticmethod
    def __go_job(curr_point: int, state: State, job: Job, route: Route) -> Optional[State]:
        """Оценка стоимости поездки на следующую задачу."""
        tt = route.matrix.travel_time[curr_point][job.location.matrix_id] + job.delay
        d = route.matrix.distance[route.storage.location.matrix_id][job.location.matrix_id]

        if not ProblemVrp.__validate_job(state.travel_time + tt, job, route):
            return None

        tmp = State(tt, d, ProblemVrp.__cost(tt, d, route), job.value.copy())
        if not ProblemVrp.__validate_courier(tmp + state, route):
            return None

        return tmp

    @staticmethod
    def __validate_job(travel_time: int, job: Job, route: Route) -> bool:
        """Проверяем, что поездка на эту задачу возможна."""
        start_time = route.start_time
        for window in job.time_windows:
            start_shift, end_shift = window.window
            if start_shift <= start_time + travel_time <= end_shift:
                return True
        return False

    @staticmethod
    def __validate_storage(travel_time: int, route: Route) -> bool:
        """Проверяем, что поездка на склад возможна."""
        start_shift, end_shift = route.storage.work_time.window
        start_time = route.start_time
        if not (start_shift <= start_time + travel_time <= end_shift):
            return False
        return True

    @staticmethod
    def __validate_courier(state: State, route: Route) -> bool:
        """Проверяем, что курьер еще жив."""

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
    def __start(route: Route) -> State:
        """Стартуем, едем от куда-то на склад."""
        distance_matrix = route.matrix.distance
        travel_time_matrix = route.matrix.travel_time
        start_id = route.courier.start_location.matrix_id
        storage_id = route.storage.location.matrix_id

        tt = travel_time_matrix[start_id][storage_id]
        d = distance_matrix[start_id][storage_id]

        cost = route.courier.cost
        c = ProblemVrp.__cost(tt, d, route) + cost.start
        return State(tt, d, c, None)

    @staticmethod
    def __end(curr_point: int, route: Route) -> State:
        """Заканчиваем, едем с последней задачи в конечную точку."""
        distance_matrix = route.matrix.distance
        travel_time_matrix = route.matrix.travel_time
        end_id = route.courier.start_location.matrix_id

        tt = travel_time_matrix[curr_point][end_id]
        d = distance_matrix[curr_point][end_id]

        return State(tt, d, ProblemVrp.__cost(tt, d, route), None)
