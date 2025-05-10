
"""
    pre01.py
        - convertir todo a minusculas
        - poner en cada linea minimo 10 palabras
    Input: ../../txt/words.txt
    Output: ../../txt/words_lowercase.txt
"""

import random

# Leer todas las palabras y convertirlas a minúsculas
with open('../../txt/words.txt', 'r', encoding='utf-8') as infile:
    palabras = [line.strip().lower() for line in infile if line.strip()]

# print(len(palabras))

# Abrir el archivo de salida
with open('../../txt/words_lowercase.txt', 'w', encoding='utf-8') as outfile:
    i = 0
    while i < len(palabras):
        # Número aleatorio de palabras por línea (entre 8 y 10)
        num_palabras =  1#random.randint(8, 10)
        # Tomamos un segmento de palabras
        linea = palabras[i:i+num_palabras]
        # Escribimos la línea unida por espacios
        outfile.write(' '.join(linea) + '\n')
        # Avanzamos el índice
        i += num_palabras