/*
	^ Compile : g++ -O2 -std=c++11 -pthread hello_world.cpp -o hello_world
	^ Run: ./a.out 
*/
#include <iostream>
#include <bits/stdc++.h>
#include <fstream>
#include <cstdint>
#include <vector>
#include <thread>
#include <chrono>
using namespace std;

#define DEVELOPING "[Developing] "
const uint64_t num_threads = 4;
vector<thread> threads;
vector< unordered_map<string,int> > hash_collection(num_threads);
unordered_map<string,vector<int>> hash_identifier;

clock_t startTime;
double getCurrentTime() {
	return (double)(clock() - startTime) / CLOCKS_PER_SEC;
}

// void say_hello(uint64_t id);

void procesarArchivo(const std::string& nombreArchivo,uint64_t threadId) {
	cout <<"nameFile: " << nombreArchivo  << " hilo: "<< threadId<<  endl;
	ifstream archivo(nombreArchivo);
	string linea;
	std::chrono::time_point<std::chrono::system_clock> inicio, fin;
	if (archivo.is_open()) {
		inicio = std::chrono::system_clock::now();
		while (std::getline(archivo, linea)) {
			// istringstream ss(linea);
			// cout << "[" << nombreArchivo << "] " << linea << endl;
			// cont++;
			// wordFrecuency[linea]++;
			hash_collection[threadId][linea] = threadId;
		}
		fin = std::chrono::system_clock::now();
		auto duracion = std::chrono::duration_cast<std::chrono::milliseconds>(fin - inicio).count();
		std::cout << "Tiempo de ejecución para " << nombreArchivo << ": " << duracion << " ms" << endl;

		archivo.close();
	} else {
		std::cerr << "Error al abrir el archivo" << nombreArchivo <<std::endl;
	}
}

int main(){
	for (uint64_t id = 0; id < num_threads; id++){
		string nameArchivo = "data/english_part_" + to_string(id) + ".txt";
		// string nameArchivo = "data/en.txt";
		// string nameArchivo = "data/english_parte_0.txt";
		threads.emplace_back(procesarArchivo, nameArchivo,id);
	}


	// join each thread at the end
	for (auto& thread: threads) thread.join();

	// Merge hash collection
	cout << DEVELOPING << "Merge Hash Collection" << endl;
	startTime = clock();
	for(auto hash: hash_collection){
		for(auto it = hash.begin(); it != hash.end(); ++it){
			// cout << it->first << " " << it->second << endl;
			hash_identifier[it->first].push_back(it->second);
		}
	}
	cout << DEVELOPING << "Time to merge hash collection: " << getCurrentTime() << endl;

	// ver el tamaño de cada hash
	cout << DEVELOPING << "Size_i Hash Collection" << endl;
	startTime = clock();
	for(auto i = 0; i < hash_collection.size(); i++){
		cout << "Hash_" << i <<  " " << hash_collection[i].size() << endl;
	}
	cout << DEVELOPING << "Time to merge hash collection: " << getCurrentTime() << endl;


	cout << DEVELOPING <<"Save hash identifier" << endl;
	ofstream archivo("out/result.txt");
	startTime = clock();
	for(auto hash_col: hash_identifier){
		archivo << hash_col.first << " ";
		for(auto it = hash_col.second.begin(); it != hash_col.second.end(); ++it){
			archivo << *it << " ";
		}
		archivo << endl;
	}
	archivo.close();
	cout << DEVELOPING << "Time to save hash identifier: " << getCurrentTime() << endl;
}

// void say_hello(uint64_t id) {
// 	std::cout << "Hello from thread: " << id << std::endl;
// }
