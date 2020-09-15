import os

from models.graph.vertex import Depot
from solvers.external.converter import Task, Vehicle, generate_json, convert_json

points = [
    (55.796358, 37.615710), (55.747231, 37.569451), (55.710934, 37.644275), (55.801464, 37.669554),
    (55.801313, 37.556785), (55.741074, 37.627011), (55.756991, 37.614874), (55.767131, 37.621689),
    (55.692519, 37.535304), (55.802768, 37.398653), (55.927528, 37.843541), (55.664829, 37.845716),
    (55.814673, 37.421812), (55.709261, 37.573223), (55.703504, 37.657074), (55.711675, 37.619188),
    (55.886972, 37.485046), (55.596175, 37.532147), (55.739277, 37.590309), (55.679316, 37.494057),
]
size = len(points)
times = [(f"2020-10-01T{10 + (i % 4) * 2}:00:00Z", f"2020-10-01T{(12 + (i % 4) * 2)}:00:00Z") for i in range(size)]
delay = 300.0
value = [1, 1]

tasks = [Task(points[i], [times[i]], delay, value) for i in range(size)]
depot = Depot((55.751594, 37.616699), 360.0, 420.0)
vehicle = Vehicle('car', 'car', 'car',
                  {"fixed": 22.0, "distance": 0.0002, "time": 0.004806},
                  [10, 10], float('inf'), float('inf'),
                  f"2020-10-01T10:00:00Z", f"2020-10-01T20:00:00Z",
                  (55.745763, 37.604962), (55.751038, 37.600797))
vehicles = [(10, vehicle)]

problem_name = 'problem'
solution_name = 'solution'
generate_json(problem_name, tasks, depot, vehicles)
os.system(f'vrp-cli solve pragmatic {problem_name}.json -o {solution_name}.json -g solution.geojson')
os.remove(f'{problem_name}.json')
convert_json(solution_name)
os.remove(f'{solution_name}.json')
