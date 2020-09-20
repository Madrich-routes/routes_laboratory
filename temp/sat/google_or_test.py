from bidict import bidict
from ortools.sat.python import cp_model

statuses = bidict({
    cp_model.FEASIBLE: 'feasible',
    cp_model.OPTIMAL: 'optimal',
    cp_model.UNKNOWN: 'unknown',
    cp_model.MODEL_INVALID: 'invalid',
    cp_model.INFEASIBLE: 'infeasible',
})


# def show_error(model):
#     return ValidateCpModel(model)


class VarArraySolutionPrinterWithLimit(cp_model.CpSolverSolutionCallback):
    """
    Печатаем решения по мере их нахождения и останавливаемся через сколько-то
    """

    def __init__(self, variables, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solution_limit = limit

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()
        if self.__solution_count >= self.__solution_limit:
            print('Stop search after %i solutions' % self.__solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count


def simple_sat(find_all=True):
    """
    Самый простой пример решения проблемы
    """
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    num_vals = 3
    x = model.NewIntVar(0, num_vals - 1, 'x')
    y = model.NewIntVar(0, num_vals - 1, 'y')
    z = model.NewIntVar(0, num_vals - 1, 'z')

    # добавляем ограничения
    model.Add(x != y)

    # создаем солвер и решаем
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0  # лимит по времени в секундах
    if find_all:
        solution_printer = VarArraySolutionPrinterWithLimit([x, y, z], 5)
        status = solver.SearchForAllSolutions(model, solution_printer)
        print(f'Нашли решений {solution_printer.solution_count()}')
    else:
        status = solver.Solve(model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            print('x = %i' % solver.Value(x))
            print('y = %i' % solver.Value(y))
            print('z = %i' % solver.Value(z))

    print('Status = %s' % solver.StatusName(status))


def simple_optimization():
    model = cp_model.CpModel()

    var_upper_bound = max(50, 45, 37)

    # создаем переменные
    x = model.NewIntVar(0, var_upper_bound, 'x')
    y = model.NewIntVar(0, var_upper_bound, 'y')
    z = model.NewIntVar(0, var_upper_bound, 'z')

    # задаем ограничения на переменные
    model.Add(2 * x + 7 * y + 3 * z <= 50)
    model.Add(3 * x - 5 * y + 7 * z <= 45)
    model.Add(5 * x + 2 * y - 6 * z <= 37)

    # objective
    model.Maximize(2 * x + 2 * y + 3 * z)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print(f'Максимум функции: {solver.ObjectiveValue()}')
        print(f'x: {solver.Value(x)}')
        print(f'y: {solver.Value(y)}')
        print(f'z: {solver.Value(z)}')


# def pazzle():

if __name__ == "__main__":
    # simple_sat()
    simple_optimization()
