#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>

namespace fs = std::filesystem;

void leerArchivosDesdeCarpeta(const std::string& carpeta) {
    // Recorremos todos los archivos dentro de la carpeta
    for (const auto& entry : fs::directory_iterator(carpeta)) {
        if (entry.is_regular_file() && entry.path().extension() == ".txt") {
            std::ifstream archivo(entry.path());
            if (!archivo.is_open()) {
                std::cerr << "No se pudo abrir: " << entry.path() << std::endl;
                continue;
            }

            std::cout << "Leyendo archivo: " << entry.path().filename() << std::endl;
            std::string linea;
            while (std::getline(archivo, linea)) {
                // Procesar cada línea aquí
                std::cout << linea << std::endl;
            }

            archivo.close();
        }
    }
}

int main() {
    std::string carpeta = "../in_test";  // Cambia esto por la ruta de tu carpeta
    leerArchivosDesdeCarpeta(carpeta);
    return 0;
}
