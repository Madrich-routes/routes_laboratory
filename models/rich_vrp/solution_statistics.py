from dataclasses import dataclass


@dataclass
class SolutionStatistics:
    total_cost: float
    unassigned: int
    service_time: int
    duration: int
    waiting_time: int
    priority: int
