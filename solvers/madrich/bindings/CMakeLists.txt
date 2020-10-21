cmake_minimum_required(VERSION 3.17)

project(vrp_runner)

set(CMAKE_CXX_STANDARD 20)

add_executable(SolverRunner problems/vrp_main.cpp)

include_directories(problems)
include_directories(problems/vrp)
include_directories(problems/vrp/operators)
include_directories(problems/mdvrp)