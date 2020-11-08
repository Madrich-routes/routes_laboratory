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
        pragmatic.Job(
            id=job.id,
            skills=job.required_skills,
            deliveries=pragmatic.Delivery(
                places=[
                    pragmatic.Place.from_rich_vrp(
                        job=job,
                        index=problem.matrix.index(job)
                    )
                ],
                demand=job.amounts,
                tag=job.name,
            ),

        )

    vehicles = []
    for agent in problem.agents:
        pragmatic.Vehicle(
            type_id=agent.type.id,  # можно type.name
            vehicleIds=[agent.id],  # можно agent.name
            profile=agent.type.profile,
            capacity=agent.type.capacity_constraints,
            shifts=[
                pragmatic.Shift(
                    eraliest=tw[0],
                    s_lat=agent.start_place.lat,
                    s_lng=agent.start_place.lon,

                    end=tw[1],
                    e_lat=agent.end_place.lat,
                    e_lng=agent.end_place.lon,

                    depots=[  # TODO:!!!

                    ],
                )
                for tw in agent.time_windows
            ],

            # косты
            fixed=agent.costs.departure,
            distance=agent.costs.dist,
            time=agent.costs.time,

            skills=agent.type.skills,
        )

    profiles = [
        pragmatic.Profile(p, f'{p}_profile_type')
        for p in problem.profiles()
    ]

    return pragmatic.Problem(
        jobs=jobs,
        vehicles=vehicles,
        profiles=profiles,
    ).dump()
