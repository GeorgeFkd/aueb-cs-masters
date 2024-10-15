cmake_minimum_required(VERSION 3.29)
project(nlp_hw1_q2)

set(CMAKE_CXX_STANDARD 26)
find_package(Boost)
add_executable(nlp_hw1_q2
        levenshtein_distance.cpp)
add_executable(mergesort merge_sort.cpp)
