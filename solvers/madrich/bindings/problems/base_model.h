#ifndef MADRICH_SOLVER_BASE_MODEL_H
#define MADRICH_SOLVER_BASE_MODEL_H

#include <string>
#include <map>
#include <vector>
#include <optional>
#include <iomanip>
#include <sstream>


class Window {
public:
    std::tuple<std::size_t, std::size_t> window;

    explicit Window() = default;

    Window(const Window &window) = default;

    explicit Window(std::tuple<std::size_t, std::size_t> window);

    explicit Window(const std::string &start_t, const std::string &end_t);

    [[maybe_unused]] void print() const;
};


class Point {
public:
    std::optional<int> matrix_id = -1;
    std::tuple<float, float> point;
    [[maybe_unused]] std::optional<std::string> address;

    explicit Point() = default;

    Point(const Point &point) = default;

    explicit Point(
            std::optional<int> matrix_id,
            std::tuple<float, float> point,
            std::optional<std::string> addr = std::nullopt
    );

    [[maybe_unused]] void print() const;
};


class Cost {
public:
    float start = 0;
    float second = 0;
    float meter = 0;

    explicit Cost() = default;

    Cost(const Cost &cost) = default;

    explicit Cost(float start, float second, float meter);

    [[maybe_unused]] void print() const;
};


class Matrix {
public:
    std::string profile;
    std::vector<std::vector<int>> distance;
    std::vector<std::vector<int>> travel_time;

    explicit Matrix() = default;

    Matrix(const Matrix &matrix) = default;

    explicit Matrix(std::string profile,
                    std::vector<std::vector<int>> distance,
                    std::vector<std::vector<int>> travel_time);

    [[maybe_unused]] void print() const;
};


class State {
public:
    int travel_time = 0;
    int distance = 0;
    float cost = 0;
    std::optional<std::vector<int>> value;

    explicit State() = default;

    State(const State &state) = default;

    explicit State(int travel_time, int distance, float cost, std::optional<std::vector<int>> value = std::nullopt);

    [[maybe_unused]] void print() const;

    State operator+(const State &rhs) const;

    State &operator+=(const State &rhs);

    bool operator<(const State &rhs) const;

private:
    static std::optional<std::vector<int>> sum_values(const State &lt, const State &rt);
};


class Job {
public:
    int delay = 0;
    std::string job_id;  // unique
    std::vector<int> value;
    std::vector<std::string> skills;
    Point location = Point(01, std::tuple(0, 0), std::nullopt);  // not unique
    std::vector<Window> time_windows;

    Job() = default;

    Job(const Job &job) = default;

    Job(int delay,
        std::string job_id,
        std::vector<int> value,
        std::vector<std::string> skills,
        const Point &location,
        std::vector<Window> time_windows);

    [[maybe_unused]] void print() const;

    bool operator==(const Job &other) const;
};


class Storage {
public:
    int load = 0;
    std::string name;
    std::vector<std::string> skills;
    Point location;
    Window work_time;
    std::vector<Job> unassigned_jobs;

    explicit Storage() = default;

    Storage(const Storage &s) = default;

    explicit Storage(
            int load,
            std::string name,
            std::vector<std::string> skills,
            const Point &location,
            const Window &work_time,
            std::vector<Job> unassigned_jobs = std::vector<Job>()
    );

    [[maybe_unused]] void print() const;
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

    explicit Courier() = default;

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

    [[maybe_unused]] void print() const;

    bool operator==(const Courier &other) const;
};


#endif //MADRICH_SOLVER_BASE_MODEL_H
