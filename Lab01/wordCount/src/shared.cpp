#include "../include/shared.h"


const int NUM_WORKERS = 12;
// std::queue<Task> taskQueue;
std::vector<std::queue<Task>> taskQueues(NUM_WORKERS);

// std::mutex queueMutex;
std::vector<std::mutex> queueMutexes(NUM_WORKERS);

// std::condition_variable queueCond;
std::vector<std::condition_variable> queueConds(NUM_WORKERS);


// moodycamel::ConcurrentQueue<Task> taskQueue;


std::atomic<bool> finishedReading(false);
std::unordered_map<std::string, int> globalWordCount;
std::mutex resultMutex;
std::string PATH = "in/20GB.txt";
const size_t BLOCK_SIZE = 8e6; // 8 MB
std::vector<std::unordered_map<std::string, int>> threadWordCounts;

// DEBUG
std::unordered_map<int, int> debugThread;

