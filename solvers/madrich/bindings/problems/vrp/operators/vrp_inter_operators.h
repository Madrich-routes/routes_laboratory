#ifndef MADRICH_SOLVER_VRP_INTER_OPERATORS_H
#define MADRICH_SOLVER_VRP_INTER_OPERATORS_H

#include <base_model.h>
#include <vrp/vrp_model.h>
#include <vrp/vrp_problem.h>
#include <route_utils.h>


bool inter_swap(VrpRoute &route1, VrpRoute &route2);

bool inter_replace(VrpRoute &route1, VrpRoute &route2);

bool inter_cross(VrpRoute &route1, VrpRoute &route2);

#endif //MADRICH_SOLVER_VRP_INTER_OPERATORS_H
