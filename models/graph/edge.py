from models.graph.vertex import Vertex


class Edge:
    def __init__(
            self,
            start: Vertex,
            end: Vertex,
    ):
        self.start = start
        self.end = end

        # Гипотетические идеи
        # priority
        # является обязательным

    def distance(self) -> float:
        """
        Длина переезда
        TODO: или это будет int?
        """
        raise NotImplementedError

    def time(self):
        raise NotImplementedError

    def cost(self):
        raise NotImplementedError

    def __eq__(self, other):
        return self.descriptor == other.descriptor

    def __hash__(self):
        return hash(self.descriptor)

    def __str__(self):
        return f"({self.start}->{self.end})"

    def __repr__(self):
        return str(self)

    def __contains__(self, n: Vertex):
        """
        Инцидентна ли вершина ребру
        """
        return n in [self.start, self.end]

    @property
    def descriptor(self):
        """
        Сравнимая величина, описывающая равенство ребер
        """
        return type(self).__name__, self.start.descriptor, self.end.descriptor


