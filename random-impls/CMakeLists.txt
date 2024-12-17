cmake_minimum_required(VERSION 3.29)
project(nlp_hw1_q2)

set(CMAKE_CXX_STANDARD 26)
find_package(Boost)
add_executable(nlp_hw1_q2
        levenshtein_distance.cpp
        levenshtein_distance.h
        pybind11_wrapper.cpp)

#set(CMAKE_CXX_FLAGS "-O3 -Wall -Wextra")
add_executable(mergesort merge_sort.cpp)
add_executable(avg_perf incremental_vs_simple_avg_perf_assessment.cpp)
add_executable(dijkstra shortest_paths_in_graph.cpp)
#add_custom_target(rl-greedy ALL
#       COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/RL-hw1.py
#        COMMENT "RL Homework 1 with greedy learning agents"
#)

#add_custom_target(nlp-hw1 ALL
#        COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/NLP_1st_Assignment.py
#        COMMENT "NLP Homework 1 with N-gram Language Models"
#)