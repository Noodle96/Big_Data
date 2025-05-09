// consumer.cpp
#include "../include/consumer.h"
#include "../include/shared.h"
#include <sstream>

void worker(int id_thread) {
    while (true) {
        Task task;
        {
            // mutex cuando trabajamos con variables condicionales
            // // [0]
            // std::unique_lock<std::mutex> lock(queueMutex);
            // queueCond.wait(lock, [] { return !taskQueue.empty() || finishedReading; });

            // if (taskQueue.empty() && finishedReading)
            //     break;

            // task = taskQueue.front();
            // taskQueue.pop();


            // // [1]  
            std::unique_lock<std::mutex> lock(queueMutexes[id_thread]);
            queueConds[id_thread].wait(lock, [id_thread] {
                return !taskQueues[id_thread].empty() || finishedReading;
            });

            if (taskQueues[id_thread].empty() && finishedReading)
                break;

            task = taskQueues[id_thread].front();
            taskQueues[id_thread].pop();
        }

        
        debugThread[id_thread]++;
        std::unordered_map<std::string, int>& localCount = threadWordCounts[id_thread];  // Usar mapa local del hilo

        std::istringstream iss(task.text);
        std::string word;
        while (iss >> word) {
            ++localCount[word];
        }
        // std::unordered_map<std::string, int> localCount;
        // std::istringstream iss(task.text);
        // std::string word;
        // while (iss >> word) {
        //     ++localCount[word];
        // }

        // {
        //     std::lock_guard<std::mutex> lock(resultMutex);
        //     for (const auto& [w, c] : localCount)
        //         globalWordCount[w] += c;
        // }
    }




    // [4] con concurrentqueue
    // Task task;
    // while (!finishedReading || !taskQueue.size_approx() == 0) {
    //     if (taskQueue.try_dequeue(task)) {
    //         debugThread[id_thread]++;
    //         std::unordered_map<std::string, int>& localCount = threadWordCounts[id_thread];
    //         std::istringstream iss(task.text);
    //         std::string word;
    //         while (iss >> word) {
    //             ++localCount[word];
    //         }
    //     } else {
    //         // Espera activa leve
    //         std::this_thread::yield();
    //     }
    // }

}
