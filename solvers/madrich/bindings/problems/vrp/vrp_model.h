#ifndef MADRICH_SOLVER_VRP_MODEL_H
#define MADRICH_SOLVER_VRP_MODEL_H


#include <string>
#include <map>
#include <vector>
#include <optional>

#include "base_model.h"


class Storage {
public:
    int load = 0;
    std::string name;
    std::vector<std::string> skills;
    Point location;
    Window work_time;
    std::vector<Job> unassigned_jobs;

    Storage() = delete;

    Storage(const Storage &s) = default;

    explicit Storage(
            int load,
            std::string name,
            std::vector<std::string> skills,
            const Point &location,
            const Window &work_time,
            std::vector<Job> unassigned_jobs = std::vector<Job>()
    );

    [[maybe_unused]] [[noreturn]] void print() const;
};


class Courier {
public:
    std::string name;
    std::string profile;
    Cost cost;
    std::vector<int> value;
    std::vector<std::string> skills;
    int max_distance = 0;
    Window work_time;
    Point start_location;
    Point end_location;

    Courier() = delete;

    Courier(const Courier &courier) = default;

    Courier(std::string name,
            std::string profile,
            const Cost &cost,
            std::vector<int> value,
            std::vector<std::string> skills,
            int max_distance,
            const Window &work_time,
            const Point &start_location,
            const Point &end_location);

    [[maybe_unused]] [[noreturn]] void print() const;

    bool operator==(const Courier &other) const;
};


class Route {
public:
    int vec = 0;
    Storage storage;
    Courier courier;
    Matrix matrix;
    int start_time = 0;
    std::vector<Job> jobs;
    State state;

    Route() = delete;

    Route(const Route &route) = default;

    Route(int vec,
          int start_time,
          const Storage &storage,
          const Courier &courier,
          const Matrix &matrix,
          std::vector<Job> job = std::vector<Job>(),
          const State &state = State());

    [[maybe_unused]] [[noreturn]] void print() const;

    [[nodiscard]] int length() const;

};


class Tour {
public:
    Storage storage;
    std::vector<Route> routes;

    Tour() = delete;

    Tour(const Tour &tour) = default;

    explicit Tour(const Storage &storage);

    [[maybe_unused]] [[noreturn]] void print() const;

    State get_state();

    [[nodiscard]] int len() const;
};


#endif //MADRICH_SOLVER_VRP_MODEL_H
