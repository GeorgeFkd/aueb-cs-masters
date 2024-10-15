#include <iostream>
#include <boost/multi_array.hpp>


boost::multi_array<double,2> createProblemArray(std::string_view word1,std::string_view word2) {
    typedef boost::multi_array<double, 2> array_type;
    int dimX = word1.length();
    int dimY = word2.length();
    std::cout << "Word 1: " << word1 << "\tWord 2: " << word2 << "\n";

    //this is needed as dynamic runtime allocation of different dimensions is not allowed
    //or so it seems
    if(dimX > dimY) {
        dimY = dimX;
    }else if(dimY > dimX) {
        dimX = dimY;
    }
    assert(dimX == dimY);
    array_type A(boost::extents[dimX + 1][dimY + 1]);
    return A;
}

void initialiseArrayValues(boost::multi_array<double,2> &arr,std::string_view word1,std::string_view word2) {

    arr[0][0] = 0;
    //fill in the first row and the first column with the number of element
    for(int col = 1; col <= word1.length(); col++) {
        //first row
        arr[0][col] = col;
    }

    for(int row = 1; row<= word2.length(); row++) {
        //first column
        arr[row][0] = row;
    }
}

void fillUpArrayWithOptimalValuesForEachCase(boost::multi_array<double,2> &arr,std::string_view word1,std::string_view word2) {
    for(int row = 1; row <= word2.length(); row++) {
        for(int col = 1; col <= word1.length(); col++ ) {
            std::cout << "Checking at: [" << row << "," << col << "]\n";
            const int moveLeft = arr[row][col-1]+1;
            const int moveUp = arr[row-1][col]+1;
            const bool hasReplacementCost = word1.at(col-1) == word2.at(row-1) ? 0 : 1;
            const int moveDiag = arr[row-1][col-1]+2*hasReplacementCost;
            int choice = -1;
            //ties are broken by the order of the ifs, left > up > diag
            if(moveLeft <= moveUp && moveLeft <= moveDiag) {
                choice = moveLeft;
            }else if(moveUp <= moveLeft && moveUp <= moveDiag) {
                choice = moveUp;
            }else if(moveDiag <= moveLeft && moveDiag <= moveUp) {
                choice = moveDiag;
            }

            assert(choice != -1);
            arr[row][col] = choice;
        }
    }
}

int unrollOptimalValueFromArray(const boost::multi_array<double,2>& arr,std::string_view word1,std::string_view word2) {
    int pos_x = word2.length();
    int pos_y = word1.length();
    std::vector<std::pair<int,int>> choices;
    choices.emplace_back(pos_x,pos_y);
    while(pos_x != 0 && pos_y != 0) {
        int moveLeft = arr[pos_x][pos_y-1];
        int moveUp = arr[pos_x-1][pos_y];
        int moveDiag = arr[pos_x-1][pos_y-1];
        if(moveLeft <= moveUp && moveLeft <= moveDiag) {
            choices.emplace_back(pos_x,pos_y-1);
            pos_y = pos_y - 1;
        }else if(moveUp <= moveLeft && moveUp <= moveDiag) {
            choices.emplace_back(pos_x-1,pos_y);
            pos_x = pos_x - 1;
        }else if(moveDiag <= moveLeft && moveDiag <= moveUp) {
            choices.emplace_back(pos_x-1,pos_y-1);
            pos_x = pos_x - 1;
            pos_y = pos_y - 1;
        }
    }

    std::reverse(choices.begin(),choices.end());
    for(auto [row,col]: choices) {
        std::cout << arr[row][col] << "->";
    }
    std::cout << "\n";

    return arr[word2.length()][word1.length()];
}

//tabular dynamic programming method
int calc_levenshtein_distance_of(std::string_view word1,std::string_view word2) {

    auto A = createProblemArray(word1,word2);
    initialiseArrayValues(A,word1,word2);
    fillUpArrayWithOptimalValuesForEachCase(A,word1,word2);
    std::cout << "=======Result=======" << "\n";

    for(auto a: A) {
        for(auto b: a) {
            std::cout << b << ",";
        }
        std::cout << "\n";
    }
    int result = unrollOptimalValueFromArray(A,word1,word2);
    return result;
}

void test_against_let_rug_nl() {
    //it seems to pass those tests but does not have the exact same path
    //using https://www.let.rug.nl/~kleiweg/lev/ for test cases
    assert(calc_levenshtein_distance_of("industry","interest") == 8);
    assert(calc_levenshtein_distance_of("good","morning") == 9);
    assert(calc_levenshtein_distance_of("soylent green is people","people soiled our green") == 26);
    assert(calc_levenshtein_distance_of("hello","world") == 8);
    assert(calc_levenshtein_distance_of("understood","understand") == 4);
}

int main(int argc,char* argv[]) {
    if(argc < 3) {
        std::cout << "Usage: <program> <word1> <word2>";
        return EXIT_FAILURE;
    }
    const std::string word1 = argv[1];
    const std::string word2 = argv[2];
    std::cout << "Computing Levenshtein Distance for words: " << word1 << "<->" << word2 << "\n";
    const auto result = calc_levenshtein_distance_of(word1,word2);
    test_against_let_rug_nl();
    std::cout << "Result is: " << result << "\n";

    return 0;
}
