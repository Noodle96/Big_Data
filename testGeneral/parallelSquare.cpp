#include <iostream>
#include <vector>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>

struct Task {
    std::vector<int> numbers;
};

std::queue<Task> taskQueue;
std::vector<int> squaredResults;
std::mutex queueMutex;
std::mutex resultMutex;
std::condition_variable queueCond;
bool finishedProducing = false;
const int NUM_WORKERS = 4;

void worker(int thread_id) {
    while (true) {
        Task task;
        {
            std::unique_lock<std::mutex> lock(queueMutex);
            // adquirir el lock antes de acceder a la cola
            // El comportamiento es:
            // Si la condición NO se cumple, el hilo:
                // 🔓 Libera el mutex automáticamente.
                // 😴 Se duerme.
            // Cuando alguien hace notify_one():
                // 🔔 El hilo se despierta.
                // 🔐 Vuelve a adquirir el mutex.
                // 👀 Revisa la condición otra vez.
            // Si la condición ahora se cumple, continúa ejecutando.
            queueCond.wait(lock, [] {
                return !taskQueue.empty() || finishedProducing;
            });

            if (taskQueue.empty() && finishedProducing)
                break;

            task = taskQueue.front();
            taskQueue.pop();
        } // aqui se libera el lock

        std::cout << "[Thread " << thread_id << "] Procesando bloque: ";
        for (int num : task.numbers)
            std::cout << num << " ";
        std::cout << std::endl;

        std::vector<int> localResult;
        for (int num : task.numbers)
            localResult.push_back(num * num);

        {
            std::lock_guard<std::mutex> lock(resultMutex);
            squaredResults.insert(squaredResults.end(), localResult.begin(), localResult.end());
        }

        std::cout << "[Thread " << thread_id << "] Finalizó bloque.\n";
    }
}

void produceTasks() {
    std::vector<int> data;
    for (int i = 1; i <= 20; ++i)
        data.push_back(i);

    const int BLOCK_SIZE = 5;
    for (size_t i = 0; i < data.size(); i += BLOCK_SIZE) {
        std::vector<int> block(data.begin() + i, data.begin() + std::min(i + BLOCK_SIZE, data.size()));

        {
            std::lock_guard<std::mutex> lock(queueMutex);
            
            taskQueue.push({block});
        }
        // despierta un Hilo que esta bloqueado esperando en queueCond.wait(...)
        queueCond.notify_one();
    }

    finishedProducing = true;
    queueCond.notify_all();
}

int main() {
    std::vector<std::thread> threads;

    for (int i = 0; i < NUM_WORKERS; ++i)
        threads.emplace_back(worker, i);  // Le pasamos el ID del hilo

    produceTasks();

    for (auto& t : threads)
        t.join();

    std::cout << "\n--- Resultado Final ---\n";
    for (int result : squaredResults)
        std::cout << result << " ";
    std::cout << std::endl;

    return 0;
}
