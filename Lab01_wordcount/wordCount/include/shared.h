#ifndef SHARED_H
#define SHARED_H

#include <queue>
#include <string>
#include <unordered_map>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <iostream>
struct Task {
    std::string text;
};

// #include "concurrentqueue.h" // Para usar ConcurrentQueue
// extern moodycamel::ConcurrentQueue<Task> taskQueue;




// extern std::queue<Task> taskQueue;
extern std::vector<std::queue<Task>> taskQueues;

// extern std::mutex queueMutex;
extern std::vector<std::mutex> queueMutexes;

// extern std::mutex resultMutex; // Enfoque con resultMutex

// extern std::condition_variable queueCond;
extern std::vector<std::condition_variable> queueConds;

extern std::atomic<bool> finishedReading;
extern std::unordered_map<std::string, int> globalWordCount;
extern const int NUM_WORKERS;
extern const size_t BLOCK_SIZE;

// Cada thread tendra su propio hash
extern std::vector<std::unordered_map<std::string, int>> threadWordCounts;

// DEBUG
extern std::unordered_map<int, int> debugThread;

extern std::string PATH;
#endif
