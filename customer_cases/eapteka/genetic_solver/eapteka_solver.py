from functools import partial
from copy import deepcopy
from typing import List, Tuple, Optional
from collections import Counter
import numpy as np

from models.rich_vrp import Depot, Agent, Job, VRPSolution, Visit
from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem
from solvers.external.vrp_cli.solver import RustSolver
from solvers.external.vroom.solver import VroomSolver
from models.rich_vrp.geometries.geometry import HaversineGeometry
from models.rich_vrp.place_mapping import PlaceMapping


class EaptekaSolver:
    """
    Класс представляет собой обертку над другими солверами, позволяющую решить проблему для нескольких складов.

    Parameters
        ----------
        problem : RichVRPProblem
        solver : str - какой солвер импользуем для решения (rust, vroom)
    """

    def __init__(
        self,
        problem: RichVRPProblem,
        solver: str,
    ):
        self.problem = problem
        self.solver = solver
        self.matrix = problem.matrix

    def couriers_replace(self, depot: Depot, agents: List[Agent]):
        """
        Функция изменяет начальную точку для курьеров.

        Parameters
            ----------
            depot: Depot
            agents: List[Agent]
        """
        lat, lon = depot.lat, depot.lon
        for agent in agents:
            agent.start_place.lat, agent.start_place.lon = lat, lon
            agent.end_place.lat, agent.end_place.lon = lat, lon

    def time_between_depots(self, start: Visit, end: Visit, agent_type: str) -> int:
        """
        Функция позволяет найти время перемещения между складами.

        Parameters
            ----------
            depot: Visit
            end: Visit
            agent_type: str

        Returns
            -------
            int - время перемещения
        """
        matrix = self.matrix.geometries[agent_type].time_matrix()
        return matrix[self.matrix.index(start.place if start), self.matrix.index(end.place)]

    # TODO разделить сложную функцию
    def cut_window(
        self,
        window: Tuple[int, int],
        depot: Depot,
        loads: List[Tuple[Depot, int, Depot, int]],
        agent_type: str,
    ) -> Optional[Tuple[int, int]]:
        """
        Функция пересчета временного окна курьера.

        Parameters
            ----------
            window: Tuple[int, int]
            depot: Depot
            loads: List[Tuple[Depot, int, Depot, int]]
            agent_type: str

        Returns
            -------
            Optional[Tuple[int, int]] - новое временное окно
        """
        all_time_windows = []

        for work_time in depot.time_windows:
            start_window, end_window = window
            start_work, end_work = work_time
            # start - (work - end) - work || work - (start - end) - work
            # work - (start - work) - end || start - (work - work) - end
            if (
                start_window <= start_work <= end_window <= end_work
                or start_work <= start_window <= end_work <= end_window
                or start_work <= start_window <= end_window <= end_work
                or start_window <= start_work <= end_work <= end_window
            ):
                start_window = (
                    start_window if start_work <= start_window else start_work
                )

                end_window = end_window if end_work >= end_window else end_work
            else:
                continue
            #  изначально нам доступно все время
            time_windows = [
                start_window,
                end_window,
            ]
            for load in loads:
                start_depot, start_time, end_depot, end_time = load
                # время перемещения между складам
                start_time -= self.time_between_depots(depot, start_depot, agent_type)
                end_time += self.time_between_depots(end_depot, depot, agent_type)
                #  каждое окно меняем с учтом времени работы склада и поездки на склад
                new_time_windows = []
                for tw in time_windows:
                    start, end = tw
                    # (start - start_time) - end - end_time
                    if start <= start_time <= end <= end_time:
                        new_time_windows.append((start, start_time))
                    # (start - start_time) - (end_time - end)
                    elif start <= start_time <= end_time <= end:
                        new_time_windows.append((start, start_time))
                        new_time_windows.append((end_time, end))
                    # (start - end) - start_time - end_time || start_time - end_time - (start - end)
                    elif (
                        start <= end <= start_time <= end_time
                        or start_time <= end_time <= start <= end
                    ):
                        new_time_windows.append((start, end))

                time_windows = new_time_windows

            all_time_windows += time_windows

        return all_time_windows if all_time_windows else None

    def find_all_routes(
        self, agent: Agent, solutions: List[VRPSolution]
    ) -> List[Tuple[Depot, int, Depot, int]]:
        """
        Функция поиска всех занятых временных окон непрерывного маршрута.

        Parameters
            ----------
            agent: Agent
            solutions: List[VRPSolution]

        Returns
            -------
            List[Tuple[Depot, int, Depot, int]]
        """
        plans: List[Plan] = []  # надеемся, что в порядке времени

        for solution in solutions:
            for route in solution.routes:
                if route.agent.id == agent.id:
                    plans.append(route)
                    break

        answer: List[Tuple[Depot, int, Depot, int]] = []
        curr_depot: Optional[Depot] = None
        prev_depot: Optional[Depot] = None
        curr_start: Optional[int] = None
        prev_end: Optional[int] = None

        for plan in plans:
            if curr_start is None:
                curr_start = plan.waypoints[0].time
                prev_end = plan.waypoints[-1].time
                # хммм, точно верим, что 1? хз как достать
                prev_depot = curr_depot = plan.waypoints[1]
            else:
                this_time = plan.waypoints[0].time
                this_depot = plan.waypoints[1]
                if (this_time - prev_end) == self.time_between_depots(
                    prev_depot, curr_depot, plan.agent.type.name
                ):
                    prev_depot = this_depot
                    prev_end = plan.waypoints[-1].time
                else:
                    answer.append((curr_start, curr_depot, prev_end, prev_depot))
                    curr_start = this_time
                    curr_depot = this_depot

        return answer

    def couriers_windows(
        self, depot: Depot, solutions: List[VRPSolution], agents: List[Agent]
    ):
        """
        Функция обновления временных окон курьеров после получения решения для одного склада.
        Если у курьера зянято все рабочее время - удаляем его.

        Parameters
            ----------
            depot: Depot,
            solutions: List[VRPSolution],
            agents: List[Agent]
        """
        remove: List[Agent] = []

        for i, agent in enumerate(agents):
            # все занятые временные окна непрерывного маршрута (мб неск складов)
            loaded: List[Tuple[Depot, int, Depot, int]]
            loaded = self.find_all_routes(agent, solutions)

            flag = False
            for j in range(len(agent.time_windows)):
                # с учетом переездов
                window = self.cut_window(
                    agent.time_windows[j], depot, loaded, agent.type.name
                )
                if window is None:
                    continue
                agent.time_windows[j] = window
                flag = True

            if not flag:  # нет свободных окон
                remove.append(agent)

        for agent in remove:
            agents.remove(agent)

    def get_agent_window(self, agent: Agent, solution: VRPSolution) -> Tuple[int, int]:
        """
        Функция нахождения окна занятости курьера в текущем решении

        Parameters
            ----------
            agent: Agent
            solutions: List[VRPSolution]

        Returns
            -------
            Tuple[int, int]
        """
        start, end = -1, -1
        for route in solution.routes:
            if route.agent == agent:
                start, end = route.waypoints[0].time, route.waypoints[-1].time
                break
        return start, end

    def change_window(self, solution: VRPSolution, agents: List[Agent]):
        """
        Функция изменения временных окон после получения решения для одного склада

        Функция нахождения окна занятости курьера в текущем решении

        Parameters
            ----------
            solution: VRPSolution
            agents: List[Agent]
        """
        for agent in agents:
            start, end = self.get_agent_window(agent, solution)
            if start == -1:
                continue

            new_windows = []  # каждое окно меняем с учетом занятости населения
            for time_window in agent.time_windows:
                start_tw, end_tw = time_window
                # start_tw == start < (end < end_tw)
                if start_tw == start and end < end_tw:
                    new_windows.append((end, end_tw))
                # (start_tw < start) < (end < end_tw)
                elif start_tw < start < end < end_tw:
                    new_windows.append((start_tw, start))
                    new_windows.append((end, end_tw))
                # (start_tw < start) < end == end_tw
                elif start_tw < start and end == end_tw:
                    new_windows.append((start_tw, start))
                else:
                    raise Exception("Bad time windows")
            agent.time_windows = new_windows

    def prepare_problem(
        self,
        copy_agents: List[Agent],
        initial_jobs: List[Job],
        depot: Depot,
        fin: bool = False,
    ):
        """
        Функция подготовки проблемы к запуску на текущий склад

        Parameters
            ----------
            copy_agents: List[Agent]
            initial_jobs: List[Job]
            depot: Depot
            fin = False: bool - финальная ли это версия проблемы
        Returns
            -------
        """
        self.problem.agents = copy_agents
        if fin:
            self.problem.jobs = initial_jobs
        else:
            self.problem.jobs = [job for job in initial_jobs if depot in job.depots]
        places = [depot] + list(self.problem.jobs)
        points = np.array([[p.lat, p.lon] for p in places])

        profile_geometries = {
            "driver": partial(HaversineGeometry, default_speed=15),
            "pedestrian": partial(HaversineGeometry, default_speed=1.5),
        }
        geometries = {
            'driver': profile_geometries['driver'](points),
            'pedestrian': profile_geometries['pedestrian'](points),
        }
        self.problem.matrix = PlaceMapping(places=places, geometries=geometries)

    def get_master_solution(
        self, solutions: List[VRPSolution], problem: RichVRPProblem
    ) -> Optional[List[VRPSolution]]:
        """
        Функция собирает из разрозненных солюшенов для каждого склада единый солюшен. В результате получаем полное решение.

        Parameters
            ----------
            solutions: List[VRPSolution]
            problem: RichVRPProblem

        Returns
            -------
            List[VRPSolution]
        """
        if len(solutions) > 0:
            info = solutions[0].info
            routes = solutions[0].routes
            for i in range(1, len(solutions)):
                info["cost"] += solutions[i].info["cost"]
                info["distance"] += solutions[i].info["distance"]
                info["duration"] += solutions[i].info["duration"]
                info["times"]["break"] += solutions[i].info["times"]["break"]
                info["times"]["driving"] += solutions[i].info["times"]["driving"]
                info["times"]["serving"] += solutions[i].info["times"]["serving"]
                info["times"]["waiting"] += solutions[i].info["times"]["waiting"]
                routes += solutions[i].routes
            master_solution = VRPSolution(problem=problem, routes=routes, info=info)
            return master_solution
        else:
            return None

    def solve(self) -> VRPSolution:
        """
        Функция запуска солвера для каждого склада отдельно. В результате получаем полное решение.

        Parameters
            ----------

        Returns
            -------
            VRPSolution
        """
        solutions: List[VRPSolution] = []
        if self.solver == "rust":
            solver_engine = RustSolver()
        # elif self.solver == "vroom":
        #     solver_engine = VroomSolver()
        else:
            raise Exception("Bad solver")
        # запоминаем изначальных курьеров
        initial_agents = deepcopy(self.problem.agents)
        initial_jobs = deepcopy(self.problem.jobs)
        for depot in self.problem.depots:
            copy_agents = deepcopy(initial_agents)
            # замена точка старта\конца на место текущего склада
            self.couriers_replace(depot, copy_agents)
            # меняем окна с учетом текущего склада и пред. склада
            self.couriers_windows(depot, solutions, copy_agents)
            # подготавливаем задачу
            self.prepare_problem(copy_agents, initial_jobs, depot)
            # запуск солвера, для текущего склада
            solution = solver_engine.solve(self.problem)
            # убираем занятое время из доступного времени в оригиналах
            self.change_window(solution, initial_agents)
            solutions.append(solution)

        # собираем финальный солюшн
        self.prepare_problem(initial_agents, initial_jobs, self.problem.depots[0], True)
        fin_solution = self.get_master_solution(solutions, self.problem)
        return fin_solution
