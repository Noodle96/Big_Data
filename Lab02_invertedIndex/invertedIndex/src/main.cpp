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
    threadInvertedIndex.resize(NUM_WORKERS);
    // std::cout << taskQueues.size() << std::endl;
    // std::cout << queueMutexes.size() << std::endl;
    // std::cout << queueConds.size() << std::endl;
    // std::cout << NUM_WORKERS << std::endl;
    
    std::vector<std::thread> threads;
    for (int i = 0; i < NUM_WORKERS; ++i)
        threads.emplace_back(worker, i);

    std::cout << "producer iniciando\n";
    producer();

    std::cout << "Producción terminada\n";
    for (auto& t : threads)
        t.join();
    std::cout << "Todos los hilos han terminado\n";
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    // MERGE threadIndexInverted[i]
    for (const auto& localMap : threadInvertedIndex) {
        for (const auto& [word, listFiles] : localMap) {
            globalInvertedIndex[word].insert(listFiles.begin(), listFiles.end());
        }
    }

    std::cout << "Tiempo de ejecución: " << duration.count() << " s\n";

    // GUARDAR globalInvertedIndex
    std::ofstream outputFile("out/invertedIndex.txt", std::ios::out);
    if (outputFile.is_open()) {
        for (const auto& [word, listFiles] : globalInvertedIndex) {
            outputFile << word << ": [";
            for (const auto& filename : listFiles) {
                outputFile << filename << " ";
            }
            outputFile << "]\n";
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
/*
enfoque [0]: 8e6 cada hilo tiene su propia cola
    309 seg => 5min 9 seg
*/