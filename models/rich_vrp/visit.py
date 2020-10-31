from dataclasses import dataclass

from models.rich_vrp.job import Job


@dataclass
class Visit:
    __slots__ = ('job', 'time')

    def __str__(self):
        return f'Visit({self.job.lon} {self.job.lat}, {self.time / 3600:.2f}ч)'

    job: Job
    time: int
