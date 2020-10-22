cmake_minimum_required(VERSION 3.17)

project(solver)

set(CMAKE_CXX_STANDARD 20)

add_executable(SolverRunner problems/vrp_main.cpp
        problems/base_model.h problems/base_model.cpp
        problems/generators.h problems/generators.cpp
        problems/vrp/vrp_improve.h problems/vrp/vrp_improve.cpp
        problems/vrp/vrp_model.h problems/vrp/vrp_model.cpp
        problems/vrp/vrp_problem.h problems/vrp/vrp_problem.cpp
        problems/route_utils.h problems/route_utils.cpp
        problems/vrp/operators/vrp_insert_job.h problems/vrp/operators/vrp_insert_job.cpp
        problems/vrp/operators/vrp_inter_operators.h problems/vrp/operators/vrp_inter_operators.cpp
        problems/vrp/operators/vrp_intra_operators.h problems/vrp/operators/vrp_intra_operators.cpp)

include_directories(problems)
include_directories(problems/vrp)
include_directories(problems/vrp/operators)
include_directories(problems/mdvrp)