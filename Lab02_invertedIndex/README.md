# Laboratorio 02: invertedIndex

Este proyecto implementa un índice invertido multithread en C++ que recibe como entrada múltiples archivos `.txt` y genera como salida un archivo `invertedIndex.txt` que contiene, para cada palabra, los archivos en los que aparece.

## Caracteristicas
- Lectura en bloques (`BLOCK_SIZE`) configurable para rendimiento.
- Cada hilo tiene:
    - Su propia cola de tareas
    - Su propio índice invertido local (`unordered_map<string, set<string>>`)
    - Se hace merge al final en una estructura global para la salida final.
    - Control de sincronización usando `std::mutex` y `std::condition_variable` para cada hilo.

## Estructura del Proyecto
```text
├── include/
│ ├── shared.h
│ ├── producer.h
│ └── consumer.h
├── src/
│ ├── main.cpp
│ ├── shared.cpp
│ ├── producer.cpp
│ └── consumer.cpp
├── in/
│ └── file01.txt
│ └── file02.txt
│ └── file03.txt
│ └── .
│ └── .
├── out/
│ ├── indexInverted.txt
│ └── debugThread.txt
├── Makefile
└── README.md
```

## Ejecución
```text
make clean
make
sudo ./clean_cache_run_invertedIndex.sh
```

## Salida
`out/invertedIndex.txt`
```text
you: [file01.tx file03.txt]
should: [file02.tx file03.txt file04.tx file06.txt]
not: [file01.tx file04.txt]
only: [file02.tx file05.txt file06.txt]
cpy: [file01.tx file05.txt]
```
`out/debugThread.txt`
```text
Thread 0: 156
Thread 1: 162
...
```
