#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <ranges>
#include <vector>
#include <chrono>
#include <random>
#include <fstream>
typedef std::mt19937 MyRng;
uint32_t seed_val = 213123956;
MyRng rng;
std::normal_distribution<double> normal_dist(0,1);


double number_generator() {
    // return normal_dist(rng);
    return 5.0;
}
long double average(const double* values, const int length) {
    double sum = 0;
    for(int i=0; i< length; i++) {
        sum += values[i];
    }
    return sum/length;
}


/// ο περισσότερος χρόνος φαίνεται να σπαταλιέται στο να γεμίσουμε την δομή δεδομένων παρά να κάνουμε απλά το άθροισμα,
/// ένα επιπλέον benefit αυτής της μεθόδου είναι ότι δεν υπάρχουν θέματα precision αφού
/// δεν υπολογίζουμε global sum το οποίο μπορεί ανάλογα την περίπτωση να φτάνει σε πολύ μεγάλα νούμερα
/// αλλά παραμένουμε στην τάξη μεγέθους που είναι ο μέσος όρος και όχι το άθροισμα
/// αν έχουμε όλα τα δεδομένα σε μια δομή πάντως βγαίνει πάνω κάτω το ίδιο
///
/// επιπλέον μπορεί να δεχτεί καλύτερα τα optimization flags ο απλός τρόπος.
///
/// είναι μια σωστή σύγκριση των αλγορίθμων αυτή?(από άποψη απόδοσης) --> γιατί εδώ φαίνεται ότι αν αγνοήσουμε την τοποθέτηση
/// στην δομή δεδομένων, θέλουν πάνω κάτω τον ίδιο χρόνο.
/// με manual memory allocation φαίνεται να θέλει περισσότερο χρόνο η incremental
/// κάτι το οποίο είναι αντιληπτό βλέποντας ότι το incremental κάνει n διαιρέσεις
/// ενώ το απλό κάνει μία στο τέλος, και η διαίρεση κοστίζει σημαντικά περισσότερο.
/// από άποψη μνήμης είναι σίγουρα χειρότερο, επίσης ο άλλος αλγόριθμος επιτρέπει
/// καλύτερο streaming και δίνει ενδιάμεσα αποτελέσματα που μπορεί σε κάποια
/// σενάρια να είναι χρήσιμο, π.χ. σε κάτι realtime.
/// η μνήμη είναι ο μόνος λόγος που είναι κακός ο απλός τρόπος, υπολογιστικά μια χαρά είναι.
std::pair<double,std::chrono::duration<double>> normal_avg(int elems) {
    //4 seconds for 10mil points
    // auto start = std::chrono::high_resolution_clock::now();

    //using arr instead of vector speeds it up a lot.
    //TODO, implement it with a vector and a .reserve() call.
    auto const start = std::chrono::high_resolution_clock::now();
    auto* rewardsOfAction = new double[elems];
    // rewardsOfAction.reserve(elems);
    for(int i = 0; i < elems ; i++) {
        rewardsOfAction[i] = number_generator();
    }
    auto const result = average(rewardsOfAction,elems);
    delete [] rewardsOfAction;
    auto const finish = std::chrono::high_resolution_clock::now();
    return {result,finish-start};
}

std::pair<double,std::chrono::duration<double>> incremental_avg(int elems) {
    double q_k1 = 0;
    const auto start = std::chrono::high_resolution_clock::now();

    for(int i = 1; i <= elems; i++) {
        const double generated = number_generator();
        q_k1 = q_k1 + (generated - q_k1)/i;
    }
    const auto finish = std::chrono::high_resolution_clock::now();
    return {q_k1,finish-start};

}

#define MAX_VAL 100000000000

int main(int argc, char *argv[]) {
    rng.seed(seed_val);
    if(argc < 2) {
        std::cout <<"Usage: <executable> <samples>" << "\n";
        return EXIT_FAILURE;
    }
    auto outputFilename = "results.csv";
    // const long n = std::stol(argv[1]);
    std::cout << "Will compare the simple average method to the incremental implementation for samples of 10 to " << MAX_VAL << "samples." << "\n";
    std::ofstream csvFile;
    csvFile.open(outputFilename);
    if(csvFile.is_open()) {
        auto headers = "Problem Size,Simple Average Time,Incremental Average Time\n";
        csvFile << headers;
    }
    for(long n = 10000; n < MAX_VAL; n = n * 10) {

        auto [result,exec_time] = normal_avg(n);
        std::cout << "Problem size: " << n << "\n";
        std::cout << "Naive avg method had time: " << exec_time << "\n";
        std::cout << "Result from naive method: " << result << "\n";
        auto [result2,exec_time2] = incremental_avg(n);
        std::cout << "Incremental avg method had time: " << exec_time2 << "\n";
        std::cout << "Result from incremental method: " << result2 << "\n";
        assert(result == result2);
        csvFile << n << "," << exec_time << "," << exec_time2 << "\n";
    }
    return 0;
}


