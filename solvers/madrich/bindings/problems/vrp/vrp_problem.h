#ifndef MADRICH_SOLVER_VRP_PROBLEM_H
#define MADRICH_SOLVER_VRP_PROBLEM_H

#include <string>
#include <map>
#include <vector>
#include <iomanip>

#include "vrp_model.h"


class VrpProblem {
public:
    static Tour
    init_tour(int vec,
              Storage &storage,
              std::vector<Courier> &couriers,
              std::map<std::string, Matrix> &matrices);

    static Route
    init_route(int vec,
               Tour &tour,
               const Courier &courier,
               std::map<std::string, Matrix> &matrices);

    static std::optional<State> get_state(const Route &route);

private:
    static bool validate_skills(const Job &job, const Courier &courier);

    static bool validate_skills(const Storage &storage, const Courier &courier);

    static bool validate_job(int travel_time, const Job &job, const Route &route);

    static bool validate_storage(int travel_time, const Route &route);

    static bool validate_courier(const State &state, const Route &route);

    static float cost(int travel_time, int distance, const Route &route);

    static std::optional<State> start(const Route &route);

    static std::optional<State> end(int curr_point, const State &state, const Route &route);

    static std::optional<State> go_job(int curr_point, const State &state, const Job &job, const Route &route);

    static std::optional<State> go_storage(int curr_point, const State &state, const Route &route);

    static std::optional<State> next_job(int curr_point, const State &state, const Job &job, const Route &route);
};

#endif //MADRICH_SOLVER_VRP_PROBLEM_H
