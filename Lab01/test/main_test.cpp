/*
==========================================================
|  Archivo       : main.cpp
|  Autor         : Russell
|  Fecha         : 2025-04-17 20:01
|--------------------------------------------------------
|  Tópicos utilizados:
|  - unordered_map
|  - string
==========================================================
*/

#include <bits/stdc++.h>
#define all(x) x.begin(),x.end()
using namespace std;

const size_t BLOCK_SIZE = 1e5; // puedes ajustar este tamaño
std::unordered_map<std::string, int> wordCount;
void solve1(){
    std::ifstream file("../wordCount/in/20GB.txt", std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "No se pudo abrir el archivo.\n";
        return;
    }

    
    char buffer[BLOCK_SIZE];
    // std::cout << "Tamaño de buffer: " << sizeof(buffer) << " bytes\n";
    std::string leftover;  // para guardar la palabra cortada al final del bloque
    int timesReadDisk = 0;
    while (file.read(buffer, BLOCK_SIZE) || file.gcount() > 0) {
        timesReadDisk++;
        // cout << "vez numero: " << timesReadDisk << endl;
        // cout << "buffer: " << buffer << " file.gcount(): " << file.gcount() << endl;
        size_t bytesRead = file.gcount();
        std::string chunk = leftover + std::string(buffer, bytesRead);
        // cout << "chunk: " << chunk << "<-s->: " << chunk.size()<< endl;

        // Si el bloque leído no termina en un espacio o salto de línea, guardamos la parte incompleta
        // y la procesamos después
        size_t lastSpace = chunk.find_last_of(" \n");
        // cout << "lastSpace: " << lastSpace << endl;
        if (lastSpace == std::string::npos) {
            leftover = chunk;  // no encontramos separadores, asumimos palabra incompleta
            continue;
        }

        std::string toProcess = chunk.substr(0, lastSpace + 1);
        leftover = chunk.substr(lastSpace + 1);  // guardar lo que quedó incompleto
        // cout << "toProcess: " << toProcess << " size: " << toProcess.size() << endl;
        // cout << "leftover: " << leftover << " size: " << leftover.size() << endl;
        std::istringstream iss(toProcess);
        std::string word;
        while (iss >> word) {
            ++wordCount[word];
        }
    }

    // procesar la última palabra si quedó algo
    if (!leftover.empty()) {
        std::istringstream iss(leftover);
        std::string word;
        while (iss >> word) {
            ++wordCount[word];
        }
    }
    // cout << "veces que entro al disco solve1: " << timesReadDisk << endl;

    // Mostrar resultados (puedes cambiar esto por guardarlo en archivo si es muy grande)
    // for (const auto& [word, count] : wordCount) {
    //     std::cout << word << ": " << count << '\n';
    // }
}

void solve2(){
    std::ifstream file("../txt/2GB.txt", std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "No se pudo abrir el archivo.\n";
        return;
    }
    string line;
    int vecesEntroDisco = 0;
    // leer linea por linea
    while (getline(file, line)) {
        // procesar la línea
        // cout << "line: " << line << endl;
        // std::istringstream iss(line);
        // std::string word;
        // while (iss >> word) {
        //     ++wordCount[word];
        // }
        vecesEntroDisco++;
    }
    cout << "veces que entro al disco solve2: " << vecesEntroDisco << endl;
}

int main(){
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    #ifdef DEBUG
        freopen("input.txt","r",stdin);
        freopen("output.txt","w",stdout);
    #endif

    // auto inicio = std::chrono::high_resolution_clock::now();
    // solve1();
    // auto fin = std::chrono::high_resolution_clock::now();
    // std::chrono::duration<double> duracion = fin - inicio;
    // std::cout << "Tiempo de ejecución: " << duracion.count() << " s\n";
    auto inicio2 = std::chrono::high_resolution_clock::now();
    solve1();
    auto fin2 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duracion2 = fin2 - inicio2;
    std::cout << "Número total de palabras distintas: " << wordCount.size() << "\n";

    std::cout << "Tiempo de ejecución: " << duracion2.count() << " s\n";
    return 0;
}

// para 20GB demora:
    //1°: 637 segundos => 10min 37 segundos
    //2°  590 segundos => 9min 50 segundos
    // limpiando page cache
    //3°: 619 segundos => 10min 19segundos
    // 565 segundos