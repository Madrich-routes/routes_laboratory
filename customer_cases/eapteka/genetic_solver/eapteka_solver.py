from copy import deepcopy
from typing import List, Tuple, Optional

from models.rich_vrp import Depot, Agent, VRPSolution
from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem
from solvers.external.vrp_cli.solver import RustSolver
from solvers.external.vroom.solver import VroomSolver


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

    def time_between_depots(self, start: Depot, end: Depot) -> int:
        """
        Функция позволяет найти время перемещения между складами.

        Parameters
            ----------
            depot: Depot
            end: Depot

        Returns
            -------
            int - время перемещения
        """
        return self.problem.matrix.time(
            self.problem.matrix.place(self.problem.depots.index(start)),
            self.problem.matrix.place(self.problem.depots.index(end)),
        )

    # TODO разделить сложную функцию
    def cut_window(
        self,
        window: Tuple[int, int],
        depot: Depot,
        loads: List[Tuple[Depot, int, Depot, int]],
    ) -> Optional[Tuple[int, int]]:
        """
        Функция пересчета временного окна курьера.

        Parameters
            ----------
            window: Tuple[int, int]
            depot: Depot
            loads: List[Tuple[Depot, int, Depot, int]]

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
                start_time -= self.time_between_depots(depot, start_depot)
                end_time += self.time_between_depots(end_depot, depot)
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
                if route.agent == agent:
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
                    prev_depot, curr_depot
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
                window = self.cut_window(agent.time_windows[j], depot, loaded)
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

    def solve(self) -> List[VRPSolution]:
        """
        Функция запуска солвера для каждого склада отдельно. В результате получаем полное решение.

        Parameters
            ----------

        Returns
            -------
            List[VRPSolution]
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
            # запуск солвера, для текущего склада
            self.problem.agents = copy_agents
            self.problem.jobs = [job for job in initial_jobs if depot in job.depots]
            solution = solver_engine.solve(self.problem)
            # убираем занятое время из доступного времени в оригиналах
            self.change_window(solution, initial_agents)
            solutions.append(solution)

        return solutions
