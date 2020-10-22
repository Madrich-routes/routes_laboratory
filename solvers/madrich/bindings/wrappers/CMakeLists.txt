cmake_minimum_required(VERSION 2.8.12)
project(madrich_solver)
set(PYBIND11_CPP_STANDARD /std:c++latest)

add_subdirectory(../pybind11)
pybind11_add_module(madrich_solver wrapper.cpp)