#include "../include/producer.h"
#include "../include/shared.h"
#include <fstream>
#include <string>
#include <iostream>
#include <mutex>

void producer() {
    // std::cout << "BLOX_SIZE: " << BLOCK_SIZE << std::endl;
    // std::cout << "PATH: " << PATH << std::endl;
    std::ifstream file(PATH, std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "No se pudo abrir el archivo.\n";
        return;
    }

    char buffer[BLOCK_SIZE];
    std::string leftover;
    int currentQueue = 0;

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
           taskQueues[currentQueue].push({toProcess});
        }
        queueConds[currentQueue].notify_one();
        currentQueue = (currentQueue + 1) % NUM_WORKERS;


        // [4]
        // taskQueue.enqueue({toProcess});  // Lock-free

    }
    // // [0]
    // if (!leftover.empty()) {
    //     std::lock_guard<std::mutex> lock(queueMutex);
    //     taskQueue.push({leftover});
    //     queueCond.notify_one();
    // }
    // finishedReading = true;
    // queueCond.notify_all();


    // // [1]
    if (!leftover.empty()) {
       std::lock_guard<std::mutex> lock(queueMutexes[currentQueue]);
       taskQueues[currentQueue].push({leftover});
       queueConds[currentQueue].notify_one();
    }
    finishedReading = true;
    for (auto& cond : queueConds)
        cond.notify_all();

    // // [4] Lock-free
    // if (!leftover.empty()) {
    //     taskQueue.enqueue({leftover});
    // }
    // finishedReading = true;
}
