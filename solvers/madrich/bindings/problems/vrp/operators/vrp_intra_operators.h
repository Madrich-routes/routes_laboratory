#ifndef MADRICH_SOLVER_VRP_INTRA_OPERATORS_H
#define MADRICH_SOLVER_VRP_INTRA_OPERATORS_H

#include <vrp/vrp_model.h>
#include <route_utils.h>
#include <vrp/vrp_problem.h>


bool three_opt(VrpRoute &route);

bool two_opt(VrpRoute &route);

#endif //MADRICH_SOLVER_VRP_INTRA_OPERATORS_H
