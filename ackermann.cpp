#include <iostream>
using namespace std;


short ackermann(short a, short b, short v){
    if(a == 0) return b + 1;
    else if(a == 1) return b + v + 1;
    else if(a == 2) return (b + 2) * v + (b + 1);
    else if(b == 0) return ackermann(a - 1, v, v);
    else return ackermann(a - 1, ackermann(a, b - 1, v), v);
}

int check_ack() {
    for(int i = 0; i < 32768; i++){
        cout << "Checking: " << i << "..." << endl;
        int result = ackermann(4, 1, i) % 32768;
        if(result == 6) {
            return i;
        }
    }
    return -1;
}

int main() {
    int result = check_ack();
    cout << "Magic Teleportation Number:     ";
    cout << "~~~" << result << "~~~" << endl;
}