from utils.printing import round_to_n


class Vertex:
    """
    Самый общий класс вершины графа маршрутизации.
    Здесь все величины должны задаваться в максимально общем виде.
    """

    def __init__(
            self,
            id: object,
            demand: float,
            work_time: float,
    ):
        self._id = id
        self.demand = demand

    def __repr__(self):
        return f"vertex<{self.id},s{self.demand}>"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(self.descriptor)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.descriptor == other.descriptor

    def __lt__(self, other):
        return str(self.descriptor) < str(other.descriptor)

    # def type(self):
    #     """
    #     TODO: очень спорный вопрос, нужно это или нет. Можно изи рассинхронится.
    #     """
    #     raise NotImplementedError

    @property
    def descriptor(self):
        """
        Репрезентация вершины, через кторую определяется равенство вершин.
        Дескриптор уникален у каждой вершины в системе.
        """
        return type(self).__name__, self._id

    @property
    def id(self):
        """
        Заданная пользователем описывалсяка для вершин.
        Id можно только получать, менять его нельзя
        """
        return self._id


class Depot(Vertex):
    """
    Вершина, которая является депо. (А нам это вообще нужно?)
    """
    pass
