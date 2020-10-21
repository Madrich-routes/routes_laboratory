#ifndef MADRICH_SOLVER_VRP_IMPROVE_H
#define MADRICH_SOLVER_VRP_IMPROVE_H

#include "vrp_problem.h"
#include "vrp_utils.h"
#include "operators/vrp_insert_job.h"
#include "operators/vrp_inter_operators.h"
#include "operators/vrp_intra_operators.h"


bool inter_improve(Tour &tour, bool post_cross);

bool intra_improve(Tour &tour, bool post_three_opt);

bool unassigned_insert(Tour &tour);

Tour improve_tour(Tour &tour, bool cross = false, bool three_opt = false);

#endif //MADRICH_SOLVER_VRP_IMPROVE_H
