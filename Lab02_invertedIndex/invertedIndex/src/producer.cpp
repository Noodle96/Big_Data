#include "../include/producer.h"
#include "../include/shared.h"
#include <fstream>
#include <string>
#include <iostream>
#include <mutex>
#include <filesystem>

namespace fs = std::filesystem;

void producer() {
    const std::string carpeta = "in/";
    int currentQueue = 0;
    for (const auto& entry : fs::directory_iterator(carpeta)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".txt") continue;

        std::ifstream file(entry.path(), std::ios::in | std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "No se pudo abrir: " << entry.path() << std::endl;
            continue;
        }
        std::cout << "\t[INFO] Leyendo archivo: " << entry.path().filename() << std::endl;
        char buffer[BLOCK_SIZE];
        std::string leftover;
        std::string filename = entry.path().filename().string();

        while (file.read(buffer, BLOCK_SIZE) || file.gcount() > 0) {
            size_t bytesRead = file.gcount();
            std::string chunk = leftover + std::string(buffer, bytesRead);

            size_t lastSpace = chunk.find_last_of(" \n");
            if (lastSpace == std::string::npos) {
                leftover = chunk;
                continue;
            }

            std::string toProcess = chunk.substr(0, lastSpace + 1);
            leftover = chunk.substr(lastSpace + 1);
            // [0]
            // {
            //     std::lock_guard<std::mutex> lock(queueMutex);
            //     taskQueue.push({toProcess});
            // }
            // queueCond.notify_one();

            // [1]
            {
                std::lock_guard<std::mutex> lock(queueMutexes[currentQueue]);
                taskQueues[currentQueue].push({toProcess, filename});
            }
            queueConds[currentQueue].notify_one();
            currentQueue = (currentQueue + 1) % NUM_WORKERS;

            // [4]
            // taskQueue.enqueue({toProcess});  // Lock-free
        } // end while

        // // [0]
        // if (!leftover.empty()) {
        //     std::lock_guard<std::mutex> lock(queueMutex);
        //     taskQueue.push({leftover});
        //     queueCond.notify_one();
        // }

        // [1]
        if (!leftover.empty()) {
            std::lock_guard<std::mutex> lock(queueMutexes[currentQueue]);
            taskQueues[currentQueue].push({leftover, filename});
            queueConds[currentQueue].notify_one();
        }

        // // [4] Lock-free
        // if (!leftover.empty()) {
        //     taskQueue.enqueue({leftover});
        // }
        file.close();
    }//end for

    //[0]
    // finishedReading = true;
    // queueCond.notify_all();

    // [1]
    finishedReading = true;
    for (auto& cond : queueConds)
        cond.notify_all();

    // [4]
    // finishedReading = true;
}
