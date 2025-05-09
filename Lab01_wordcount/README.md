# WordCount Multihilo en C++

Este proyecto implementa un sistema eficiente de conteo de palabras usando múltiples hilos en C++. Procesa archivos de gran tamaño (por ejemplo, 20GB) y distribuye bloques de texto a **una cola individual por hilo** para evitar la contención de recursos y mejorar el rendimiento, además tratamos las palabras cortadas.

## Caracteristicas
- Productor (`producer.cpp`): Lee el archivo en bloques (`BLOCK_SIZE`), divide el texto por espacios y distribuye tareas entre las colas de los hilos en forma circular.
- Consumidor (`consumer.cpp`): Cada hilo consume tareas de su propia cola. Cuenta las palabras en un `unordered_map` local.
- Main (`main.cpp`):
- Lanza los hilos consumidores.
- Llama al productor.
- Espera que los hilos terminen.
- Fusiona los mapas locales de conteo.
- Guarda la salida final.

## Paralelismo
- Usa `std::thread` para lanzar `NUM_WORKERS` hilos.
- Cada hilo tiene:
    - Su propia cola de tareas (`taskQueues[i]`)
    - Su propio mapa local (`threadWordCounts[i]`)
- Comunicación mediante `std::condition_variable` y `std::mutex` por hilo.

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
│ └── 20GB.txt
├── out/
│ ├── wordCount.txt
│ └── debugThread.txt
├── Makefile
└── README.md
```

## Ejecución
```text
make clean
make
sudo ./clean_cache_run_wordcount.sh
```

## Salida
`out/wordCount.txt`
```text
you: 123456
should: 112233
not: 84321
only: 5678
cpy: 123
```
`out/debugThread.txt`
```text
Thread 0: 156
Thread 1: 162
...
```
