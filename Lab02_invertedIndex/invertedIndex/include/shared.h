#ifndef SHARED_H
#define SHARED_H

#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <set>
#include <mutex>
#include <condition_variable>
#include <atomic>

struct Task {
    std::string text;
    std::string filename;
};

// #include "concurrentqueue.h" // Para usar ConcurrentQueue
// extern moodycamel::ConcurrentQueue<Task> taskQueue;

// extern std::queue<Task> taskQueue;
extern std::vector<std::queue<Task>> taskQueues;

// extern std::mutex queueMutex;
extern std::vector<std::mutex> queueMutexes;

// extern std::condition_variable queueCond;
extern std::vector<std::condition_variable> queueConds;

extern std::atomic<bool> finishedReading;
extern std::unordered_map<std::string, std::set<std::string> > globalInvertedIndex;
extern const int NUM_WORKERS;
extern const size_t BLOCK_SIZE;

// Cada thread tendra su propio hash
// key: word
// value: set of filenames
extern std::vector<std::unordered_map<std::string, std::set<std::string>>> threadInvertedIndex;

// DEBUG
extern std::unordered_map<int, int> debugThread;
#endif
