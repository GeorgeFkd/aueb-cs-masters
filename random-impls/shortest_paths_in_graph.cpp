//
// Created by georgefkd on 2/11/2024.
//

#include <iostream>
#include <utility>

#include "boost/graph/adjacency_list.hpp"
#include "boost/graph/adjacency_matrix.hpp"
#include "boost/graph/dijkstra_shortest_paths.hpp"


class NodeT {
public:
    int id;
    std::string name;
    NodeT(const int id,std::string name) : id(id),name(std::move(name)){}
    NodeT() : id(0),name("empty2"){}
};

class EdgeT {
public:
    int cost;
    explicit EdgeT(const int cost) : cost(cost){}
    EdgeT() : cost(-1){}
    [[nodiscard]] int costOf() const {
        return cost;
    }
};




int main(int argc,char* argv[]) {
    int N = 100;
    typedef boost::adjacency_list<boost::listS,boost::vecS,boost::directedS,NodeT,EdgeT> Graph;
    Graph G(N);
    auto vA = boost::add_vertex(G);
    G[vA] = NodeT(1,"A");

    auto vB = boost::add_vertex(G);
    G[vB] = NodeT(2,"B");

    auto vC = boost::add_vertex(G);
    G[vC] = NodeT(3,"C");

    auto vD = boost::add_vertex(G);
    G[vD] = NodeT(4,"D");

    auto vE = boost::add_vertex(G);
    G[vE] = NodeT(5,"E");

    boost::add_edge(vA,vB,EdgeT(4),G);
    boost::add_edge(vA,vC,EdgeT(2),G);
    boost::add_edge(vB,vC,EdgeT(3),G);
    boost::add_edge(vC,vB,EdgeT(1),G);
    boost::add_edge(vB,vD,EdgeT(2),G);
    boost::add_edge(vB,vE,EdgeT(3),G);
    boost::add_edge(vC,vD,EdgeT(4),G);
    boost::add_edge(vC,vE,EdgeT(5),G);
    boost::add_edge(vE,vD,EdgeT(1),G);

    std::vector<int> distances(boost::num_vertices(G));
    std::vector<Graph::vertex_descriptor> predecessors(boost::num_vertices(G));

    // for (const auto& v : boost::make_iterator_range(vertices(G))) {
    //     const NodeT& node = G[v];
    //     std::cout << "Vertex ID: " << node.id << ", Name: " << node.name << "\n";
    // }
    std::cout << "Shortest distances from vertex 0:" << std::endl;
    for (std::size_t i = 0; i < distances.size(); ++i) {
        std::cout << "Distance to vertex " << i << ": " << distances[i] << std::endl;
    }

    // Output the shortest path tree
    std::cout << "\nShortest path tree:" << std::endl;
    for (std::size_t i = 0; i < predecessors.size(); ++i) {
        if (i != vA) { // Skip the source vertex
            std::cout << "Vertex " << i << " via " << predecessors[i] << std::endl;
        }
    }




}