from formats.pragmatic import pragmatic
from models.rich_vrp.problem import RichVRPProblem


def dumps_problem(
    problem: RichVRPProblem,
) -> str:
    """Сохраняем RichVRPProblem в pragmatic формате, для последующего решения rust солвером.

    TODO: учесть цену job. Учесть много доставок и пикапов

    Parameters
    ----------
    problem : RichVRPProblem

    Returns
    -------
    Строку, содержащую pragmatic-описание проблемы
    """

    jobs = []
    for job in problem.jobs:
        # временно! придумть глобальное решение, ибо (имхо) все солверы тут хотят int
        amounts = [int(job.amounts[0] * 1000), int(job.amounts[1] * 1000000)]
        new_job = pragmatic.Job(
            id=str(job.id),
            deliveries=[
                pragmatic.Delivery(
                    places=[
                        pragmatic.Place.from_rich_vrp(
                            job=job, index=problem.matrix.index(job)
                        )
                    ],
                    demand=amounts,
                    tag=str(job.name) if str(job.name) != "nan" else "",
                )
            ],
        )
        if len(
            job.required_skills
        ):  # временное решение, проработать в соответствии с докой
            new_job["skills"] = job.required_skills
        jobs.append(new_job)

    vehicles = []
    for agent in problem.agents:
        # TODO: временно! придумть глобальное решение, ибо (имхо) все солверы тут хотят int
        capacity = [
            int(agent.type.capacity_constraints[0] * 1000),
            int(agent.type.capacity_constraints[1] * 1000000),
        ]
        agent.time_windows = pragmatic.convert_tw(agent.time_windows)
        vehicle = pragmatic.Vehicle(
            typeId=str(agent.type.id) + str(agent.id),  # можно type.name
            vehicleIds=[str(agent.id)],  # можно agent.name
            profile=agent.type.profile,
            capacity=capacity,
            shifts=[
                pragmatic.Shift(
                    earliest=str(tw[0]),
                    s_lat=agent.start_place.lat,
                    s_lng=agent.start_place.lon,
                    end=str(tw[1]),
                    e_lat=agent.end_place.lat,
                    e_lng=agent.end_place.lon,
                    depots=[],  # TODO:!!!
                )
                for tw in agent.time_windows
            ],
            # косты
            fixed=agent.costs.departure,
            distance=agent.costs.dist,
            time=agent.costs.time,
            skills=agent.type.skills,
        )
        if len(
            agent.type.skills
        ):  # TODO: временное решение, проработать в соответствии с докой
            vehicle["skills"] = agent.type.skills
        vehicles.append(vehicle)

    profiles = [pragmatic.Profile(p, f"{p}_profile_type") for p in problem.profiles()]
    return pragmatic.Problem(
        jobs=jobs,
        vehicles=vehicles,
        profiles=profiles,
    ).dump()
