#include <iostream>
#include <string>

int main() {
    std::string s;
    std::cout << "Tamaño máximo de un string (en bytes): " << s.max_size() << std::endl; // aprox 4e18 Bytes => 4e12 MB
    return 0;
}
