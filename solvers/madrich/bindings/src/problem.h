#ifndef MADRICH_PROBLEM_H
#define MADRICH_PROBLEM_H

#include <string>
#include <map>
#include <vector>
#include <algorithm>

#include <iostream>
#include <iomanip>


typedef std::vector <std::vector<int>> array;
typedef std::vector <std::vector<double>> array_d;

typedef std::vector<int> vec_i;
typedef std::vector<double> vec_d;


class Window {
public:
    std::tuple<int, int> window;

    Window();

    Window(const Window &w);

    Window(std::tuple<int, int> w);

    void print();

    std::tuple<int, int> get_seconds();

private:
    static int __to_sec(int t);
};


class Point {
public:
    std::optional<int> matrix_id;
    std::tuple<float, float> point;
    std::optional <std::string> address;

    Point();

    Point(const Point &p);

    Point(std::optional<int> mi, std::tuple<float, float> p, std::optional <std::string> a);

    void print();
};


class Cost {
public:
    float start;
    float second;
    float meter;

    Cost();

    Cost(const Cost &c);

    Cost(float st, float s, float m);

    void print();
};


class Matrix {
public:
    std::string profile;
    array distance;
    array travel_time;

    Matrix();

    Matrix(const Matrix &m);

    Matrix(std::string p, array d, array tt);

    void print();
};


class Storage {
public:
    std::string name;
    int load;
    std::vector <std::string> skills;
    Point location;
    Window work_time;

    Storage();

    Storage(const Storage &s);

    Storage(std::string n, int l, std::vector <std::string> ss, Point ln, Window wt);

    void print();
};


class Job {
public:
    std::string job_id;  // unique
    std::optional <Storage> storage;
    int delay;
    std::vector<int> value;
    std::vector <std::string> skills;
    Point location;  // not unique
    std::vector <Window> time_windows;

    Job();

    Job(const Job &j);

    Job(std::string ji,
        std::optional <Storage> s,
        int d,
        std::vector<int> v,
        std::vector <std::string> ss,
        Point l,
        std::vector <Window> tw);

    void print();

    bool operator==(const Job &other);
};


class Courier {
public:
    std::string name;
    std::string profile;
    Cost cost;
    std::vector<int> value;
    std::vector <std::string> skills;
    int max_distance;
    Window work_time;
    Point start_location;
    Point end_location;

    Courier();

    Courier(const Courier &c);

    Courier(std::string n, std::string p, Cost c, std::vector<int> v, std::vector <std::string> ss, int md, Window wt,
            Point sl, Point el);

    void print();

    bool operator==(const Courier &other);
};


class State {
public:
    int travel_time;
    int distance;
    float cost;
    std::optional <std::vector<int>> value;

    State();

    State(const State &s);

    State(int tt, int d, float c, std::optional <std::vector<int>> v);

    void print();

    const State operator+(const State &other);

    State &operator+=(const State &other);

    bool operator<(const State &other);

private:
    static std::optional <std::vector<int>> __value(State lt, State rt);
};


class Route {
public:
    Storage storage;
    Courier courier;
    Matrix matrix;
    int start_time;
    std::vector <Job> jobs;
    int travel_time;
    int distance;
    float cost;

    Route();

    Route(const Route &r);

    Route(Storage s, Courier c, Matrix m, int st, std::vector <Job> j, int tt, int d, float ct);

    void print();

    void save_state(State state);

    Route new_route(std::vector <Job> jobs);

    int len();

};


class Tour {
public:
    Storage storage;
    std::vector <Route> routes;
    std::vector <Job> unassigned_jobs;
    //Problem& problem;

    Tour();

    Tour(const Tour &t);

    Tour(Storage s, std::vector <Route> r, std::vector <Job> ujs);

    void print();

    State get_state();

    int len_jobs();

    int len();
};


class Problem {
public:
    Tour init(Storage storage, std::vector <Job> jobs, std::vector <Courier> couriers);

    virtual std::optional <State> get_state(Route *route);
};

class ClassicProblem : public Problem //
{
public:
    Tour init(Storage storage, std::vector <Job> jobs, std::vector <Courier> couriers,
                     std::map <std::string, Matrix> matrices);

    std::optional <State> get_state(Route *route);

private:
    static bool __validate_skills(Job obj, Courier courier);

    static bool __validate_skills(Storage obj, Courier courier);

    static float __cost(int travel_time, int distance, Route route);

    static State __start(Route route);

    static bool __validate_job(int travel_time, Job job, Route route);

    static std::optional <State> __go_job(int curr_point, State state, Job job, Route route);

    static bool __validate_storage(int travel_time, Route route);

    static std::optional <State> __go_storage(int curr_point, State state, Route route);

    static std::optional <State> __next_job(int curr_point, State state, Job job, Route route);

    static State __end(int curr_point, Route route);

    static bool __validate_courier(State state, Route route);

    static Route __greedy_route(Storage storage, std::vector <Job> jobs, Courier courier,
                                std::map <std::string, Matrix> matrices);

    static Tour __greedy_tour(Storage storage, std::vector <Job> jobs, std::vector <Courier> couriers,
                              std::map <std::string, Matrix> matrices);
};

#endif //MADRICH_PROBLEM_H
