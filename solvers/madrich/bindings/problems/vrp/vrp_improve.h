#ifndef MADRICH_SOLVER_VRP_IMPROVE_H
#define MADRICH_SOLVER_VRP_IMPROVE_H

#include <vrp_problem.h>
#include <route_utils.h>
#include <operators/vrp_insert_job.h>
#include <operators/vrp_inter_operators.h>
#include <operators/vrp_intra_operators.h>


bool inter_improve(VrpTour &tour, bool post_cross);

bool intra_improve(VrpTour &tour, bool post_three_opt);

bool unassigned_insert(VrpTour &tour);

VrpTour improve_tour(VrpTour &tour, bool cross = false, bool three_opt = false);

#endif //MADRICH_SOLVER_VRP_IMPROVE_H
