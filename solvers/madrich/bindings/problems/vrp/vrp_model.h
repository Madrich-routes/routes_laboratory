#ifndef MADRICH_SOLVER_VRP_MODEL_H
#define MADRICH_SOLVER_VRP_MODEL_H

#include <string>
#include <map>
#include <vector>
#include <optional>
#include <base_model.h>


class VrpRoute {
public:
    int vec = 0;
    Storage storage;
    Courier courier;
    Matrix matrix;
    int start_time = 0;
    std::vector<Job> jobs;
    State state;

    explicit VrpRoute() = default;

    VrpRoute(const VrpRoute &route) = default;

    VrpRoute(int vec,
             int start_time,
             const Storage &storage,
             const Courier &courier,
             const Matrix &matrix,
             std::vector<Job> job = std::vector<Job>(),
             const State &state = State());

    [[maybe_unused]] void print() const;
};


class VrpTour {
public:
    Storage storage;
    std::vector<VrpRoute> routes;

    explicit VrpTour() = default;

    VrpTour(const VrpTour &tour) = default;

    explicit VrpTour(const Storage &storage);

    bool inter_improve(bool post_cross);

    bool intra_improve(bool post_three_opt);

    bool unassigned_insert();

    void improve_tour(bool cross = false, bool three_opt = false);

    [[maybe_unused]] void print() const;

    State get_state();

private:
    int phase = 0;
    std::map<std::string, bool> previous_phase;
    std::map<std::string, bool> current_phase;

    void check_block();

    void update_phase();

    void mark_route(bool value, const VrpRoute &route);

    void mark_route(bool value, const VrpRoute &route1, const VrpRoute &route2);

    bool check_route(const VrpRoute &route);
};


#endif //MADRICH_SOLVER_VRP_MODEL_H
