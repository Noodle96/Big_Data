#include "../include/producer.h"
#include "../include/consumer.h"
#include "../include/shared.h"
#include <thread>
#include <vector>
#include <iostream>
#include <fstream>
#include <chrono>



int main() {
    auto start = std::chrono::high_resolution_clock::now();
    // std::cout << NUM_WORKERS << std::endl;
    std::vector<std::thread> threads;
    for (int i = 0; i < NUM_WORKERS; ++i)
        threads.emplace_back(worker, i);

    producer();

    for (auto& t : threads)
        t.join();

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "Tiempo de ejecución: " << duration.count() << " s\n";
    std::cout << "Número total de palabras distintas: " << globalWordCount.size() << "\n";

    // GUARDAR wordcount
    std::ofstream outputFile("out/wordCount.txt", std::ios::out);
    if (outputFile.is_open()) {
        for (const auto& [word, count] : globalWordCount) {
            outputFile << word << ": " << count << '\n';
        }
        outputFile.close();
    } else {
        std::cerr << "No se pudo abrir el archivo de salida.\n";
    }

    // DEBUG TREAD
    std::ofstream debugFileThread("out/debugThread.txt", std::ios::out);
    long long FileSizeTest = 0;
    if( debugFileThread.is_open()){
        for (const auto& [threadId, count] : debugThread) {
            debugFileThread << "Thread " << threadId << ": " << count << '\n';
            FileSizeTest += count;
        }
        FileSizeTest *= BLOCK_SIZE;
        FileSizeTest /= 1024 * 1024; // Convertir a MB
        debugFileThread << "Tamaño test: " << FileSizeTest << " MB\n";
        debugFileThread.close();
    } else {
        std::cerr << "No se pudo abrir el archivo de salida de debugFileThread.\n";
    }
    // DEBUG WORD COUNT
    return 0;
}
