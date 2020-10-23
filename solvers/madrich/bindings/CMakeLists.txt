cmake_minimum_required(VERSION 2.8.12)
project(cmake_example)
set(PYBIND11_CPP_STANDARD /std:c++latest)

add_subdirectory(pybind11)
pybind11_add_module(Tour src/wrapper.cpp)