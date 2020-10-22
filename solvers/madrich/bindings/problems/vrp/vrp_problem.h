#ifndef MADRICH_SOLVER_VRP_PROBLEM_H
#define MADRICH_SOLVER_VRP_PROBLEM_H

#include <string>
#include <map>
#include <vector>
#include <iomanip>
#include <string>
#include <cstdlib>
#include <vrp_model.h>


class VrpProblem {
public:
    static VrpTour
    init_tour(int vec,
              Storage &storage,
              std::vector<Courier> &couriers,
              std::map<std::string, Matrix> &matrices);

    static VrpRoute
    init_route(int vec,
               VrpTour &tour,
               const Courier &courier,
               std::map<std::string, Matrix> &matrices);

    static std::optional<State> get_state(const VrpRoute &route);

private:
    static bool validate_skills(const Job &job, const Courier &courier);

    static bool validate_skills(const Storage &storage, const Courier &courier);

    static bool validate_job(int travel_time, const Job &job, const VrpRoute &route);

    static bool validate_storage(int travel_time, const VrpRoute &route);

    static bool validate_courier(const State &state, const VrpRoute &route);

    static float cost(int travel_time, int distance, const VrpRoute &route);

    static std::optional<State> start(const VrpRoute &route);

    static std::optional<State> end(int curr_point, const State &state, const VrpRoute &route);

    static std::optional<State> go_job(int curr_point, const State &state, const Job &job, const VrpRoute &route);

    static std::optional<State> go_storage(int curr_point, const State &state, const VrpRoute &route);

    static std::optional<State> next_job(int curr_point, const State &state, const Job &job, const VrpRoute &route);
};

#endif //MADRICH_SOLVER_VRP_PROBLEM_H
