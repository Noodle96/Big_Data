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
using namespace std;

const uint64_t num_threads = 4;
std::vector<thread> threads;

void say_hello(uint64_t id);

void procesarArchivo(const std::string& nombreArchivo) {
	cout << "nameFile: " << nombreArchivo << endl;
	ifstream archivo(nombreArchivo);
	string linea;
	if (archivo.is_open()) {
		while (std::getline(archivo, linea)) {
			// istringstream ss(linea);
			// cout << "[" << nombreArchivo << "] " << linea << endl;
		}
		archivo.close();
	} else {
		std::cerr << "Error al abrir el archivo" << nombreArchivo <<std::endl;
	}
}

int main(){
	for (uint64_t id = 0; id < num_threads; id++){
		string nameArchivo = "data/archivo_part_" + to_string(id) + ".txt";
		threads.emplace_back(procesarArchivo, nameArchivo);
	}


	// join each thread at the end
	for (auto& thread: threads) thread.join();
}

void say_hello(uint64_t id) {
	std::cout << "Hello from thread: " << id << std::endl;
}