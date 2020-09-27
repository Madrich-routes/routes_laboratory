from typing import Optional

from models.simulation.depot import Depot


class SimutationAgent:
    dummy_car: 'SimutationAgent' = None

    def __init__(
            self,
            cid: int,
            start_time: Optional[int],
            end_time: Optional[int],
            depot_point: Depot,
            car_type: Optional[CarType] = None
    ) -> None:
        self.type = ...  # TODO:

        assert self.start_time is not None and self.end_time is not None, "Время == None"

        self.depot_point: Depot = depot_point

        self.type: Optional[CarType] = car_type

        self.containers: List = []

        self.is_active: bool = True  # в работе ли машинапше
        self.current_price: float = 0.0
        self.current_weight: float = 0.0  # текущая масса в машине
        self.current_volume: float = 0.0  # текущий объем без прессовки
        self.current_distance: float = 0.0  # пройденное расстояние на текущий момент
        self.current_time: int = self.start_time  # Текущее время в секундах для машины

        self.way_points: List[Visit] = [self.create_depot_visit(self.current_time)]

        self.id_ = cid
        self.driver_id: Optional[int] = None
        self.problem: "Optional[VRPProblem]" = None

    def __str__(self):
        try:
            depot_time = self.time_to_depot()
            landfill_time = self.time_to_landfill()
        except Exception:
            depot_time = -1
            landfill_time = -1

        return (
            f'Car(id:{self.id_}, тип:{self.type}, точка:{self.current_point}, '
            f'путь:{self.current_distance / 1000:.1f}км, время:{self.current_time / 3600:.2f}ч, '
            f'объем:{self.current_volume}, точек:{len(self.way_points)}, '
            f'до депо:{depot_time:.2f}ч, до выгрузки:{landfill_time:.2f}ч), '
            f'поддерживаемые типы {list(self.type.allowed_container_types)}, '
            f'конец рабочего дня {self.end_time / 3600:.2f} '
        )

    def __lt__(self, other):
        return self.id_ < other.id_

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.id_.__hash__()

    def __eq__(self, other):
        return self.id_ == other.id

    @staticmethod
    def copy_attrs(src: 'SimutationAgent', dst: 'SimutationAgent') -> None:
        """
        Копируем всю изменяемую информацию из одной машины в другую
        """
        immutable_attrs = ("is_active", 'current_price', 'current_volume',
                           'current_weight', 'current_distance', 'current_time')

        for a in immutable_attrs:
            setattr(dst, a, getattr(src, a))

        dst.containers = src.containers[:]
        dst.way_points = src.way_points[:]

    def is_empty(self):
        return self.current_volume == 0 and self.current_weight == 0 and len(self.containers) == 0

    def goto_landfill(self) -> 'SimutationAgent':
        assert not (not self.is_bunker_car() and self.is_empty()), 'Разгружаем пустую машину'

        self.move_to(self.problem.landfill_point)
        self.current_time += self.problem.landfill_point.work_time
        self.current_weight = 0
        self.current_volume = 0
        self.containers = []

        return self

    def goto_depot(self) -> 'SimutationAgent':
        if isinstance(self.current_point, Depot):
            return self

        if not isinstance(self.current_point, Landfill) and not self.is_empty():
            self.goto_landfill()  # выгрузить машину, если нужно

        self.move_to(point=self.depot_point)

        if self.current_time > self.end_time:
            raise ValueError(f"Опоздаем в депо "
                             f"{self.current_time / 3600:.2f}/{self.end_time / 3600:.2f}ч")

        assert \
            abs(self.current_volume) < 0.001 \
            or abs(self.current_weight) < 0.001 \
            or len(self.containers) == 0, \
            'Едем на базу не пустыми!'

        if self.can_take_containers():
            assert \
                isinstance(self.way_points[-2].point, Landfill) \
                and isinstance(self.way_points[-1].point, Depot), \
                'Последние 2 точки должны быть (Landfill, Depot)'

        self.is_active = False
        return self

    def atomic_goto_depot(self) -> 'SimutationAgent':
        """
        Аналогично goto_depot, но в случае ошибки состояние не меняется
        """
        SimutationAgent.copy_attrs(self, SimutationAgent.dummy_car)
        try:
            return self.goto_depot()
        except ValueError as e:
            SimutationAgent.copy_attrs(SimutationAgent.dummy_car, self)
            raise e

    # время от дистанции
    def get_duration(self, path) -> float:
        return self.type.calculate(distance=path)[1]

    # во сколько будет на точке
    # @lru_cache()
    def get_eta(self, point: Point) -> float:
        path = self.problem.distance(self.current_point, point)  # расстояние до заявки

        duration = self.get_duration(path)  # время до заявки
        return self.current_time + duration

    def finish_time(self, point: 'Container') -> int:
        """ Когда будем на базе """
        assert point.point_type == 'container'
        duration = 0
        duration += self.score_path(self.current_point, point)  # расстояние до заявки
        duration += self.score_path(point, self.problem.landfill_point)  # расстояние до заявки
        duration += self.score_path(self.problem.landfill_point, self.depot_point)  # расстояние до заявки

        duration += point.type_work_time
        duration += self.problem.landfill_point.work_time

        return self.current_time + duration

    # Можем ли мы взять конкретный реквест
    def pickup_problems(self, con: 'Container') -> Union[bool, str]:
        if self.is_bunker_car():
            return False if self.slow_check_can_take(con) else "Этот бункеровоз не затащит"

        problems = (
            lambda: self.will_overfill(con) * "Перегруз",

            lambda:
            (not con.is_car_compatible(self)) *
            f"Несовместимый тип {con.type_id} not in {sorted(self.type.allowed_container_types)}",

            lambda:
            self.will_overwork(con) *
            f"Будет переработка {self.finish_time(con) / 3600:.2f}/{self.end_time / 3600:.2f}",

            lambda: (not con.is_time_ok(self.get_eta(con))) * "Не в окне",
            lambda: (not self.is_active) * "Неактивна",
        )

        for problem in problems:
            p = problem()
            if p:
                return p

        return False

    def is_compatible(self, con: 'Container') -> bool:
        problems = (
            self.will_overfill(con),
            not con.is_car_compatible(self),
        )

        return not any(problems)

    # слишком много точек
    def too_many_points(self) -> bool:
        return len(self.containers) >= self.type.max_places_by_trip

    def slow_check_can_take(self, con: 'Container') -> bool:
        """ Проверяем можем ли взять """
        try:
            test_copy = copy.deepcopy(self)  # пробуем на липовой машине
            test_copy.take_bunker(con)
            test_copy.goto_depot()
        except ValueError as e:
            return False
        return True

    # слишком долгий маршрут
    def will_overwork(self, con) -> bool:
        problems = (
            self.finish_time(con) > self.end_time,  # так как бывает 0 или None
            len(self.way_points) + 1 > self.type.max_places_by_trip,
        )

        return any(problems)

    # машина переполнится
    def will_overfill(self, con: 'Container') -> bool:
        problems = (
            self.current_volume + con.capacity > self.type.max_volume,
            self.current_weight + 0 > self.type.max_weight,  # noqa
        )

        return any(problems)

    #  взять реквест
    def take(self, con: 'Container') -> Tuple:
        m_stats = self.move_to(con)
        r_stats = self.score_request(con)
        self.update_stats(*r_stats)

        self.current_volume += con.capacity
        self.current_weight += 0  # noqa (потом он будет)

        self.containers += [con]

        return tuple(sum(p) for p in zip(m_stats, r_stats))

    def take_returnable(self, con: 'Container') -> 'SimutationAgent':
        """ Логика по взятию контейнера """
        self.take(con)
        self.goto_landfill()
        self.move_to(con)

        return self

    def take_usual_bunker(self, con: 'Container') -> 'SimutationAgent':
        # если мы только что из возвратного, надо сгонять в landfill, взять контейнер
        if (
                len(self.way_points) > 1
                and self.way_points[-1].point.point_type == 'container'
                and self.way_points[-1].point.must_return
        ):
            self.goto_landfill()

        self.take(con)
        self.goto_landfill()

        return self

    def take_bunker(self, con: 'Container') -> 'SimutationAgent':
        if con.type_is_replacement:
            self.take_returnable(con)
        else:
            self.take_usual_bunker(con)

        return self

    def time_to_landfill(self) -> float:
        return self.dist_to(self.problem.landfill_point) / self.type.speed_avg / 3600

    def time_to_depot(self) -> float:
        return self.dist_to(self.depot_point) / self.type.speed_avg / 3600

    # доехать до точки
    def move_to(self, point: Point) -> Tuple[float, float, float]:
        assert self.is_active, 'Пытаемся куда-то ехать на неактивной машине'

        stats = self.score_move(point)
        self.update_stats(*stats)

        self.way_points += [Visit(point, self.current_time)]

        return stats

    # оценить ресурсы на перемещение машины в данную точку
    def score_move(self, point: Point) -> Tuple[float, float, float]:
        path = self.dist_to(point)

        return self.type.calculate(
            distance=path,
            departure=(self.current_point == self.depot_point),
        )

    def score_path(self, p1: Point, p2: Point) -> float:
        return self.type.calculate(
            distance=self.problem.distance(p1, p2),
            loads=0
        )[1]

    # оценить затраты кроме перемещения
    def score_request(self, dr: 'Container') -> Tuple[float, float, float]:
        assert dr.point_type == 'container'
        return self.type.calculate(
            loads=1,
            load_time=dr.type_work_time
        )  # погрузки

    # расстояние до точки
    def dist_to(self, point: Point) -> float:
        return self.problem.distance(self.current_point, point)

    # обновить текущую статистику машины
    def update_stats(self, distance: float, duration: int, price: float) -> 'SimutationAgent':
        self.current_distance += distance
        self.current_price += price
        self.current_time += duration
        return self

    # Добавить группу точек. При недопустимых значениях будет брошено ValueError
    def add_containers(self, containers) -> 'SimutationAgent':
        for r in containers:  # пытаемся добавить каждый реквест
            p = self.pickup_problems(r)  # проверяем, что можем взять заявку
            if p:  # проверяем, что можем взять заявку
                raise ValueError(p)
            else:
                self.take(r)
        return self

    def atomic_add_containers(self, containers: Iterable['Container']) -> 'SimutationAgent':
        SimutationAgent.copy_attrs(self, SimutationAgent.dummy_car)
        try:
            self.add_containers(containers)
            success = SimutationAgent._get_dummy()
            SimutationAgent.copy_attrs(self, success)
            self.goto_depot()
            SimutationAgent.copy_attrs(success, self)
        except ValueError as e:
            SimutationAgent.copy_attrs(SimutationAgent.dummy_car, self)
            raise e
        return self

    # проверяем возможность обработки заявок
    def can_process(self, containers: Iterable['Container']) -> bool:
        SimutationAgent.copy_attrs(self, SimutationAgent.dummy_car)
        try:
            self.add_containers(containers)
            self.goto_depot()
            return True
        except ValueError:
            return False
        finally:
            SimutationAgent.copy_attrs(SimutationAgent.dummy_car, self)

    # проверяем возможность обработки заявок
    def adding_problems(self, containers: Iterable['Container']) -> str:
        SimutationAgent.copy_attrs(self, SimutationAgent.dummy_car)
        try:
            self.add_containers(containers)
            self.goto_depot()
            return ''
        except ValueError as e:
            return str(e)
        finally:
            SimutationAgent.copy_attrs(SimutationAgent.dummy_car, self)

    def time_left(self) -> float:
        return (self.end_time - self.current_time) / 3600

    def is_bunker_car(self) -> bool:
        return self.type.operation_mode == OperationMode.BUNKER

    def is_portal_car(self) -> bool:
        return self.type.operation_mode == OperationMode.PORTAL

    def is_container_car(self) -> bool:
        return self.type.operation_mode == OperationMode.CONTAINER

    def can_take_containers(self) -> bool:
        return self.is_container_car() or self.is_portal_car()

    @property
    def start_point(self) -> 'Point':
        return self.way_points[0].point

    @property
    def current_point(self) -> 'Point':
        return self.way_points[-1].point

    def merge(self, other: 'SimutationAgent') -> 'SimutationAgent':
        """ Продолжение этой машины сливается в нее """
        if len(self.way_points) < 2:
            return copy.deepcopy(other)

        if len(other.way_points) < 2:
            return copy.deepcopy(self)

        res_car = copy.deepcopy(self)
        if len(res_car.way_points) > 2 and res_car.current_point.point_type == 'depot':
            res_car.undo_depot()  # отменяем последнее депо

        assert res_car.current_point == other.start_point, 'Пытаемся вмержить машину, находящуюся в другом месте'

        res_car.way_points += other.way_points[1:]
        res_car.containers += other.containers  # TODO: зачем нам вообще containers? Мб удалить?

        res_car.current_distance += other.current_distance
        res_car.current_price += other.current_price
        res_car.is_active = other.is_active
        res_car.current_time = other.current_time

        return res_car

    def transform_to_empty(self) -> 'SimutationAgent':
        """
        Получаем эту машину в этой точке и времени, но без посещейний и контейнеров
        Нужно для передачи в другие решалки с последуюшим мержем
        """
        if not self.way_points or len(self.way_points) == 1:
            return self

        new_car: SimutationAgent = copy.deepcopy(self)
        new_car.way_points = self.way_points[-1:]  # оставляем только последнюю
        new_car.containers = []

        new_car.start_time = new_car.way_points[0].time  # Текущее время в секундах для машины
        new_car.current_time = new_car.start_time

        new_car.is_active = True  # активна и только начала
        new_car.current_price = 0.0
        new_car.current_distance = 0.0

        return new_car

    def unmove(self) -> Tuple[float, float, float]:
        assert len(self.way_points) >= 2, 'Пытаемся отменить ход, который не сделали'

        removed_point, self.way_points = self.way_points[-1].point, self.way_points[:-1]

        stats = self.score_move(removed_point)
        self.update_stats(*(-s for s in stats))

        return stats

    def undo_depot(self):
        assert isinstance(self.current_point, Depot), 'Отменяем депо в которое мы не приехали'

        self.unmove()

    # def untake(self):
    #     r_stats = self.score_request(con)
    #     self.update_stats(*r_stats)
    #
    #     m_stats = self.move_to(con)
    #
    #     self.current_volume += con.capacity
    #     self.current_weight += 0  # noqa (потом он будет)
    #
    #     self.containers += [con]
    #
    #     return tuple(sum(p) for p in zip(m_stats, r_stats))

    # превращает машину в словарь
    def export(self) -> Dict[str, Any]:
        return dict(
            id=self.id_,
            price=self.current_price,
            loads=len(self.containers),
            distance=self.current_distance / 1000,  # км->метры
            disposal_requests=[dr.export() for dr in self.containers],
            way_points=tuple(wp.export() for wp in self.way_points),
            start_time=self.start_time,
            end_time=self.end_time,
            type_id=self.type_id,
            depot_point=self.depot_point.export(),
            driver_id=self.driver_id,
        )

    def create_depot_visit(self, time: int) -> Visit:
        return Visit(self.depot_point, time)

    # как будто ничего не было
    def clear_requests(self) -> 'SimutationAgent':

        self.containers = []

        self.is_active = True  # в работе ли машина
        self.current_price = 0
        self.current_weight = 0  # текущая масса в машине
        self.current_volume = 0  # текущий объем без прессовки
        self.current_distance = 0  # пройденное расстояние на текущий момент
        self.current_time = self.start_time  # Текущее время в секундах для машины

        self.way_points = [self.way_points[0]]

        return self

    def print_visits(self):
        res = str(self)
        res += '\n'
        res += '-' * 20 + '\n'

        for i, p in enumerate(self.way_points[:-1]):
            try:
                dist = self.problem.distance(self.way_points[i].point, self.way_points[i + 1].point)
                dist = round(dist / 1000, 1)
            except Exception:
                dist = 'Fail'
            res += str(self.way_points[i])
            res += f'->{dist}->'
            res += str(self.way_points[i + 1]) + '\n'

        print(res)

    @staticmethod
    def _get_dummy() -> 'SimutationAgent':
        # noinspection Mypy
        return SimutationAgent(0, 0, None, None, Null(), None)  # noqa


SimutationAgent.dummy_car = SimutationAgent._get_dummy()
