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
    threadWordCounts.resize(NUM_WORKERS);
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

    // MERGE threadWordCounts[i]
    for (const auto& localMap : threadWordCounts) {
        for (const auto& [word, count] : localMap) {
            globalWordCount[word] += count;
        }
    }

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
// [0]
/*
    BLOCK_SIZE = 2e5 && CON MAP por cada thread:
        1°: 378 seg => 6min 18seg
        2°: 316 seg => 5min 16seg
        3°: 375 seg => 6min 15seg
        4°: 439 seg => 7min 19seg
        5°: 286 seg => 4min 46seg 
    
    BLOCK_SIZE = 8e5 && CON MAP por cada thread:
        1°: 360 seg => 6min
        2°: 346 segundos => 5min 46seg
        3°: 401 segundos => 6min 41seg
        4°: 292 segundos => 4min 52seg
    ------------------------------------------------
    287 seg => 4min 47seg 8e6
    288 seg => 4min 48 seg
    
*/

// [1000]
/*
    BLOCK_SIZE = 2e5 && resultMutex
        1°: 664 seg => 11min 4seg
        2° 403 seg => 6min 43seg
        3°: 432 seg = > 7min 12seg

    BLOCK_SIZE = 8e5 && resultMutex
        1°: 691 seg => 11min 31seg
        2°: 472 sef => 7min 52seg
        3°: 506 seg => 8min 26seg
*/


// [1]
/*
    Cada Thread su cola
    437 seg => 7min 17seg
    326 seg => 5min 26seg
    344 seg => 5min 44seg
    292 seg => 4min 52 seg
    -------------------------
    282 seg => 4min 42 seg 8e6
    282 seg => 4min 42 seg 2e5
*/

// [2] x BBT
// [3] x total/BLOCK_SIZE
// [4]
/*
    con concurrentqueue
    1°: 285 seg => 4min 45seg
    2°: 287 seg => 4min 47seg
    ------------------------------
    3°: 287 seg => 4min 47 seg 2e5
    4°: 284 seg => 4min 44seg 8e6
*/
