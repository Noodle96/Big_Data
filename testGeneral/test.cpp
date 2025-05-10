#include <iostream>
using namespace std;
// #include <string>

// int main() {
//     std::string s;
//     std::cout << "Tamaño máximo de un string (en bytes): " << s.max_size() << std::endl; // aprox 4e18 Bytes => 4e12 MB
//     return 0;
// }

// string::find_last_of
// #include <iostream>       // std::cout
// #include <string>         // std::string
// #include <cstddef>         // std::size_t

// void SplitFilename (const std::string& str)
// {
//   std::cout << "Splitting: " << str << '\n';
//   std::size_t found = str.find_last_of("/\\");
//   std::cout << " path: " << str.substr(0,found) << '\n';
//   std::cout << " file: " << str.substr(found+1) << '\n';
// }

// int main ()
// {
//   // std::string str1 ("/usr/bin/man");
//   // std::string str2 ("c:\\windows\\winhelp.exe");
//   //   std::cout << "str2: " << str2  << std::endl;
//   // SplitFilename (str1);
//   // SplitFilename (str2);

//   // std::string chunk = "Hello world\nThis is a test";
//   std::string chunk = "Hello\n";
// size_t lastSpace = chunk.find_last_of(" \n");

// std::cout << "Last space or newline is at index: " << lastSpace << std::endl;
//   std::cout << "size: " << chunk.size() << std::endl;
//   return 0;
// }


int main() {
  int a = 5;

  {
      int a = 10; // Esta 'a' es distinta de la anterior
      std::cout << "a en bloque interno: " << a << std::endl;
  }

  std::cout << "a en main: " << a << std::endl;
  return 0;
}