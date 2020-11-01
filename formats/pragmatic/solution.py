from typing import Dict, List, Optional

from formats.pragmatic.utils import iget


class Activity:
    def __init__(self, d: Dict):
        self.job_id: str = d['jobId']
        self.job_type: str = d['type']
        self.job_tag: str = d.get('job_tag')

        self.lat: Optional[float] = iget(d, 'location', 'lat')
        self.lng: Optional[float] = iget(d, 'location', 'lng')

        self.start: Optional[str] = iget(d, 'time', 'start')
        self.end: Optional[str] = iget(d, 'time', 'end')


class Stop:
    def __init__(self, d: Dict):
        self.distance: int = d['distance']
        self.load: List[int] = d['load']
        self.lat: Optional[float] = iget(d, 'location', 'lat')
        self.lng: Optional[float] = iget(d, 'location', 'lng')
        self.arrival: Optional[str] = iget(d, 'time', 'arrival')
        self.departure: Optional[str] = iget(d, 'time', 'departure')
        self.activities: List[Activity] = [Activity(i) for i in d['activities']]


class Vehicle:
    def __init__(self, d: Dict):
        self.vehicle_id: str = d['vehicleId']
        self.type_id: str = d['typeId']
        self.shift_index: int = d['shiftIndex']
        self.stops: List[Stop] = [Stop(i) for i in d['stops']]

        stats = d['statistic']
        self.cost: float = stats['cost']
        self.distance: int = stats['distance']
        self.duration: int = stats['duration']

        times = stats['times']
        self.driving: int = times['driving']
        self.serving: int = times['serving']
        self.waiting: int = times['waiting']
        self.break_: int = d['statistic']['times'].get('break')


class Reason:
    def __init__(self, d: Dict):
        self.code: int = d['code']
        self.description: str = d['description']


class Unassigned:
    def __init__(self, d: Dict):
        self.job_id: str = d['jobId']
        self.reasons: List[Reason] = [Reason(i) for i in d['reasons']]


class Solution:
    def __init__(self, data):
        self.tours: List[Vehicle] = [Vehicle(i) for i in data['tours']]
        self.unassigned: List[Unassigned] = [Unassigned(i) for i in data.get('unassigned', [])]

        stats = data['statistic']
        self.cost: int = stats['cost']
        self.distance: int = stats['distance']
        self.duration: int = stats['duration']

        times = stats['time']
        self.driving: int = times['driving']
        self.serving: int = times['serving']
        self.waiting: int = times['waiting']
        self.break_: int = times.get('break')
