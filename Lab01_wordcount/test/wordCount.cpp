/*
==========================================================
|  Archivo       : wordCount.cpp
|  Autor         : Russell
|  Fecha         : 2025-04-20 16:38
|--------------------------------------------------------
|  Tópicos utilizados:
|  - Hash
|  - string
|  - thread
==========================================================
*/

#include <bits/stdc++.h>
// #include <thread>
// #include <mutex>
// #include <condition_variable>
// #include <atomic>
// #include <chrono>

using namespace std;
#define all(x) x.begin(),x.end()
#define pb push_back
#define mp make_pair

const int NUM_WORKERS = 12;
const size_t BLOCK_SIZE = 1e6;

struct Task {
    std::string text;
};

std::queue<Task> taskQueue;
std::mutex queueMutex;
std::condition_variable queueCond;

std::atomic<bool> finishedReading(false);
std::unordered_map<std::string, int> globalWordCount;
std::mutex resultMutex;

void worker() {
    while (true) {
        Task task;

        {
            std::unique_lock<std::mutex> lock(queueMutex);
            queueCond.wait(lock, [] { return !taskQueue.empty() || finishedReading; });

            if (taskQueue.empty() && finishedReading)
                break;

            task = taskQueue.front();
            taskQueue.pop();
        }

        // Contar palabras
        std::unordered_map<std::string, int> localCount;
        std::istringstream iss(task.text);
        std::string word;
        while (iss >> word) {
            ++localCount[word];
        }

        // Mezclar resultado
        {
            std::lock_guard<std::mutex> lock(resultMutex);
            for (const auto& [w, c] : localCount)
                globalWordCount[w] += c;
        }
    }
}

void solve_parallel() {
    std::ifstream file("../../txt/20GB.txt", std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "No se pudo abrir el archivo.\n";
        return;
    }

    char buffer[BLOCK_SIZE];
    std::string leftover;

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

        {
            std::lock_guard<std::mutex> lock(queueMutex);
            taskQueue.push({toProcess});
        }
        queueCond.notify_one();
    }

    if (!leftover.empty()) {
        std::lock_guard<std::mutex> lock(queueMutex);
        taskQueue.push({leftover});
        queueCond.notify_one();
    }

    finishedReading = true;
    queueCond.notify_all();
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();

    std::vector<std::thread> threads;
    for (int i = 0; i < NUM_WORKERS; ++i)
        threads.emplace_back(worker);

    solve_parallel();

    for (auto& t : threads)
        t.join();

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "Tiempo de ejecución: " << duration.count() << " s\n";
    std::cout << "Número total de palabras distintas: " << globalWordCount.size() << "\n";

    return 0;
}