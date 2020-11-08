import ujson

import settings
from models.problems.base import BaseRoutingProblem
from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from solvers.base import BaseSolver
from solvers.external.cmd import CommandRunner
from solvers.external.vroom.format import dumps_problem

input_file = "tmp/eapteka_vroom_input.json"
output_file = "tmp/eapteka_vroom_output.json"


class VroomSolver(BaseSolver):
    """Солвер, который использует vroom."""

    def __init__(self):
        ...

    def solve(
        self,
        problem: BaseRoutingProblem
    ) -> VRPSolution:
        problem_str = dumps_problem(problem=problem)

        CommandRunner(
            command=[settings.VROOM_PATH, '-i', input_file, '-o', output_file],
            input_files={input_file: problem_str},
            output_files=[output_file],
            files_dir='vroom_solver',
            base_dir='vroom_solver',
        ).run()
