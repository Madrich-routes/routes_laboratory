from models.problems.base import BaseRoutingProblem


class MatrixScaler:
    def __init__(self, max_value: int):
        self.max_value = max_value

    def transform(self, problem: BaseRoutingProblem):
        """
        Приводим матрицу к интам заданного размера,
        чтобы можно было передавать ее в разные конкретные солверы
        """
        mult = 32767 / problem.matrix.max()
        problem.matrix = (mult * problem.matrix).astype("int32")

    def restore(self):
        """
        Ничего делать не нужно у нас и так все хорошо — маршрут построен.
        """
        pass
