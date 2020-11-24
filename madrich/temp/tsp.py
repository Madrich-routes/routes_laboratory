from pyomo.core import (
    AbstractModel, Binary, Constraint, NonNegativeReals, Objective, Param, Set, Var, minimize)
# from py
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeIntegers

n = 20

# Model
mod = AbstractModel()

# Indexes for the cities
mod.points = Set(n)
mod.edges = Set(within=mod.points * mod.points)

mod.costs = Param(mod.edge, within=NonNegativeReals, mutable=True)

# Index for the dummy variable u
# mod.U = RangeSet(2, n)

# Decision variables xij
mod.x = Var(mod.edges, within=Binary)
mod.u = Var(mod.points, within=NonNegativeIntegers, bounds=(0, n - 1))  # dummy vars

mod.objective = Objective(
    sense=minimize,
    rule=lambda m: sum(m.x[e] * m.costs[e] for e in m.edges)
)

mod.rest2 = Constraint(
    mod.points,
    rule=lambda m, p: sum(m.x[p, j] for j in m.M if j != p) + sum(m.x[j, p] for j in m.M if j != p) == 2
)

mod.rest3 = Constraint(
    mod.U, mod.points,
    rule=lambda m, i, j: (m.u[i] - m.u[j] + m.x[i, j] * n <= n - 1) if i != j else (m.u[i] - m.u[i])  # noqa
)

# Решаем ее. Что там и как вообще.

mod.pprint()

# Solves
solver = SolverFactory('cbc')
result = solver.basic_solve(mod, tee=True)

# Prints the results
print(result)

List = list(mod.x.keys())
for i in List:
    if mod.x[i]() != 0:
        print(i, '--', mod.x[i]())
