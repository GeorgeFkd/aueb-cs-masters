//
// Created by georgefkd on 14/10/2024.
//


#include <iostream>
#include <vector>
void mergearr(std::vector<int>& arr,int start,int mid,int end) {
    auto lSize = mid-start+1;
    auto tempArrL = new int[lSize];
    for(int i = 0; i < lSize; i++) {
        tempArrL[i] = arr[start+i];
    }
    auto rSize = end-mid;
    auto tempArrR = new int[rSize];
    for(int i = 0; i < rSize; i++) {
        tempArrR[i] = arr[mid+1+i];
    }


    // [1,2,5,7] [3,4,6,8] -> [1,2
    int lIndex = 0;
    int rIndex = 0;
    std::vector<int> merged;merged.reserve(lSize+rSize);
    while (lIndex < lSize && rIndex < rSize) {
        if(tempArrL[lIndex] <= tempArrR[rIndex]) {
            //choose from L
            merged.push_back(tempArrL[lIndex++]);
        }else {
            //choose from R
            merged.push_back(tempArrR[rIndex++]);
        }
    }

    //get the rest of the elements in the merged version
    while(lIndex < lSize) {
        merged.push_back(tempArrL[lIndex++]);
    }
    while(rIndex < rSize) {
        merged.push_back(tempArrR[rIndex++]);
    }
    delete [] tempArrL;
    delete [] tempArrR;

    //copy the merged version to the original one
    int x = start;
    for(const int i:merged) {
        arr[x++] = i;
    }




}

[[nodiscard]] void mergesort(std::vector<int>& arr,int start,int end) {
    if(end<=start)return;
    const int m = (start+end) / 2;
    mergesort(arr,start,m);
    mergesort(arr,m+1,end);
    mergearr(arr,start,m,end);
}



int main(int argc,char* argv[]) {
    if(argc < 2) {
        std::cout << "Give a list of elements and have it sorted by merge-sort";
        return EXIT_FAILURE;
    }
    int array_size = argc-1;

    std::vector<int> arr(array_size);
    for(int i=1; i < argc; i++) {
        arr[i-1] = std::stoi(argv[i]);

    }
    std::cout << "Elements provided: " << "\n";
    for(int i = 0; i < array_size; i++) {
        std::cout << arr[i] << " ";
    }

    mergesort(arr,0,arr.size()-1);

    std::cout << "\nElements sorted: " << "\n";
    for(int i = 0; i < array_size; i++) {
        std::cout << arr[i] << " ";
    }

}
