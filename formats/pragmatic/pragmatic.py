"""
Здесь описан pragmatic формат используемый в растовском солвере
"""

import json
from dataclasses import dataclass
from typing import List, Optional

from models import rich_vrp
from models.problems.base import BaseRoutingProblem


def serialize_problem(problem: BaseRoutingProblem):
    pass


@dataclass
class Place:
    # Own
    duration: int
    times: List[List[str]]  # None

    # Location
    lat: float
    lng: float

    @classmethod
    def from_rich_vrp(cls, job: rich_vrp.Job):
        return cls(
            duration=job.delay,
            times=job.time_windows,
            lat=job.lat,
            lon=job.lon,
        )

    def dump(self):
        res = dict(
            duration=self.duration,
            location={
                'lat': self.lat,
                'lng': self.lng,
            }
        )
        if self.times is not None:
            res["times"] = self.times

        return res


@dataclass
class Pickup:
    tag: str  # None
    places: List[Place]
    demand: List[int]

    def __init__(self, places, demand, tag=None):
        # Own
        self.tag = tag
        self.places = places
        self.demand = demand

    def dump(self):
        dump_Pickup = {}
        if self.tag is not None:
            dump_Pickup["tag"] = self.tag
        dump_Pickup["demand"] = self.demand
        dump_Pickup["places"] = [i.dump() for i in self.places]
        return dump_Pickup


@dataclass
class Delivery:
    tag: str  # None
    places: List[Place]
    demand: List[int]

    def __init__(self, places, demand, tag=None):
        # Own
        self.tag = tag
        self.places = places
        self.demand = demand

    def dump(self):
        dump_Deliverie = {}
        if self.tag is not None:
            dump_Deliverie["tag"] = self.tag
        dump_Deliverie["demand"] = self.demand
        dump_Deliverie["places"] = [i.dump() for i in self.places]
        return dump_Deliverie


@dataclass
class Job:
    id: str
    deliveries: List[Delivery]  # None
    pickups: List[Pickup]  # None
    skills: List[str]  # None

    def __init__(self, id, deliveries=None, pickups=None, skills=None):
        # Own
        self.id = id
        self.deliveries = deliveries
        self.pickups = pickups
        self.skills = skills

    @classmethod
    def from_rich_vrp(cls, job: rich_vrp.Job):
        return cls(
            id=job.id,

            duration=job.delay,
            times=job.time_windows,
            lat=job.lat,
            lon=job.lon,
        )

    def dump(self):
        dump_Job = {}
        dump_Job["id"] = self.id
        if self.deliveries is not None:
            dump_Job["deliveries"] = [i.dump() for i in self.deliveries]

        if self.pickups is not None:
            dump_Job["pickups"] = [i.dump() for i in self.pickups]

        if self.skills is not None:
            dump_Job["skills"] = self.skills

        return dump_Job


@dataclass
class Relation:
    type: str
    jobs: List[str]
    vehicleId: str

    def dump(self):
        return dict(type=self.type, jobs=self.jobs, vehicleId=self.vehicleId)


@dataclass
class Reload:
    duration: int
    lat: float
    lng: float

    def dump(self):
        return dict(
            duration=self.duration,
            location=dict(
                lat=self.lat,
                lng=self.lng
            ),
        )


@dataclass
class Break:
    time: List[str]
    duration: int

    def dump(self):
        return dict(time=self.time, duration=self.duration)


@dataclass
class Depot:
    duration: int
    lat: float
    lng: float

    def dump(self):
        return dict(
            duration=self.duration,
            location=dict(
                lat=self.lat,
                lng=self.lng
            )
        )


@dataclass
class Shift:  ########### ready +++++++
    # Own
    depots: List[Depot]  # None
    reloads: List[Reload]  # None
    breaks: List[Break]  # None

    # Start
    earliest: str

    # Start:Location
    s_lat: float
    s_lng: float

    # End # None
    latest: str  # None

    # End:Location
    e_lat: float  # None
    e_lng: float  # None

    # Latest # None
    time: str  # None

    # Latest:Location
    l_lat: float  # None
    l_lng: float  # None

    def __init__(self, earliest, s_lat, s_lng,
                 end=None, depots=None, reloads=None, breaks=None,
                 latest=None, e_lat=None, e_lng=None, time=None, l_lat=None, l_lng=None):
        # Own
        self.depots = depots
        self.reloads = reloads
        self.breaks = breaks

        # Start
        self.earliest = earliest

        # Start:Location
        self.s_lat = s_lat
        self.s_lng = s_lng

        # End
        self.latest = latest

        # End:Location
        self.e_lat = e_lat
        self.e_lng = e_lng

        # Latest
        self.time = time

        # Latest:Location
        self.l_lat = l_lat
        self.l_lng = l_lng

    def dump(self):
        dump_Shift = {}

        if self.depots is not None:
            dump_Shift["depots"] = [i.dump() for i in self.depots]

        if self.reloads is not None:
            dump_Shift["reloads"] = [i.dump() for i in self.reloads]

        if self.breaks is not None:
            dump_Shift["breaks"] = [i.dump() for i in self.breaks]

        dump_Shift["start"] = {}
        dump_Shift["start"]["earliest"] = self.earliest
        dump_Shift["start"]["location"] = {}
        dump_Shift["start"]["location"]["lat"] = self.s_lat
        dump_Shift["start"]["location"]["lng"] = self.s_lng

        if self.latest is not None:
            dump_Shift["end"] = {}
            dump_Shift["end"]["latest"] = self.latest
            dump_Shift["end"]["location"] = {}
            dump_Shift["end"]["location"]["lat"] = self.e_lat
            dump_Shift["end"]["location"]["lng"] = self.e_lng
        if self.time is not None:
            dump_Shift["Latest"] = {}
            dump_Shift["Latest"]["time"] = self.time
            dump_Shift["Latest"]["location"] = {}
            dump_Shift["Latest"]["location"]["lat"] = self.l_lat
            dump_Shift["Latest"]["location"]["lng"] = self.l_lng
        return dump_Shift


@dataclass
class Vehicle:  ############# ready ++++++++
    # Own
    typeId: str
    vehicleIds: List[str]
    profile: str
    capacity: List[int]
    skills: List[str]  # None
    shifts: List[Shift]

    # Cost
    fixed: int
    distance: float
    time: float

    def __init__(self, typeId, vehicleIds, profile,
                 capacity, shifts, fixed, distance, time, skills=None):
        # Own
        self.typeId = typeId
        self.vehicleIds = vehicleIds
        self.profile = profile
        self.capacity = capacity
        self.skills = skills
        self.shifts = shifts

        # Cost
        self.fixed = fixed
        self.distance = distance
        self.time = time

    def dump(self):
        return dict(
            typeId=self.typeId,
            vehicleIds=self.vehicleIds,
            profile=self.profile,
            capacity=self.capacity,
            skills=self.skills,
            shifts=[i.dump() for i in self.shifts],
            costs=dict(
                fixed=self.fixed,
                distance=self.distance,
                time=self.time,
            )
        )


@dataclass
class Profile:
    name: str
    type: str

    def dump(self):
        return dict(name=self.name, type=self.type)


@dataclass
class Type:
    # Own
    type_name: str

    # Options # None
    tolerance: Optional[float] = None
    threshold: Optional[float] = None

    def dump(self):
        return dict(
            type=self.type_name,
            options=dict(
                tolerance=self.tolerance,
                threshold=self.threshold,
            ),
        )


@dataclass
class Problem:
    # Plan
    jobs: List[Job]

    # Fleet
    vehicles: List[Vehicle]
    profiles: List[Profile]

    relations: List[Relation] = None
    primary: List[Type] = None
    secondary: List[Type] = None

    def __init__(self, jobs, vehicles, profiles, relations=None, primary=None, secondary=None):
        # Plan
        self.jobs = jobs
        self.relations = relations

        # Fleet
        self.vehicles = vehicles
        self.profiles = profiles

        # Objectives
        self.primary = primary
        self.secondary = secondary

    def dump(self):
        return dict(
            plan=dict(
                jobs=[i.dump() for i in self.jobs],
                relations=[i.dump() for i in self.relations]
            ),
            fleet=dict(
                vehicles=[i.dump() for i in self.vehicles],
                profiles=[i.dump() for i in self.profiles],
            ),
            objectives=dict(
                primary=[i.dump() for i in self.primary],
                secondary=[i.dump() for i in self.secondary],
            )
        )

    def dump_json(self):
        return json.dump(self.dump())
