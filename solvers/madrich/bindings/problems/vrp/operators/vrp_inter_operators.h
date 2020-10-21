#ifndef MADRICH_SOLVER_VRP_INTER_OPERATORS_H
#define MADRICH_SOLVER_VRP_INTER_OPERATORS_H

#include <base_model.h>
#include <vrp/vrp_model.h>
#include <vrp/vrp_problem.h>
#include <vrp_utils.h>

bool inter_swap(Route &route1, Route &route2);

bool inter_replace(Route &route1, Route &route2);

bool inter_cross(Route &route1, Route &route2);

#endif //MADRICH_SOLVER_VRP_INTER_OPERATORS_H
