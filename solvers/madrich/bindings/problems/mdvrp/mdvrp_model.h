#ifndef MADRICH_SOLVER_MDVRP_MODEL_H
#define MADRICH_SOLVER_MDVRP_MODEL_H

#include <base_model.h>
#include <vector>
#include <utility>


class Track {
public:
    Storage storage;
    std::vector<Job> jobs;

    [[maybe_unused]] void print() const;
};

class MdvrpRoute {
public:
    int vec = 0;
    Courier courier;
    Matrix matrix;
    int start_time = 0;
    std::vector<Track> tracks;
    State state;

    explicit MdvrpRoute() = default;

    MdvrpRoute(const MdvrpRoute &route) = default;

    MdvrpRoute(int vec,
             int start_time,
             const Courier &courier,
             const Matrix &matrix,
             std::vector<Track> tracks = std::vector<Track>(),
             const State &state = State());

    [[maybe_unused]] void print() const;

    [[nodiscard]] int assigned_jobs() const;
};

class MdvrpTour {
public:
    std::vector<Storage> storages;
    std::vector<MdvrpRoute> routes;

    explicit MdvrpTour() = default;

    MdvrpTour(const MdvrpTour &tour) = default;

    explicit MdvrpTour(std::vector<Storage> storages);

    State get_state();

    [[maybe_unused]] void print() const;
};

#endif //MADRICH_SOLVER_MDVRP_MODEL_H
