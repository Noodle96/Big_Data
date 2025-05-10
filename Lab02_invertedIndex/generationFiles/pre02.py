"""
    Tamaño objetivo	            Veces a repetir aprox.
    2GB (2048MB)	            2048 / 4.63 ≈ 443 veces
    4GB (4096MB)	            4096 / 4.63 ≈ 884 veces
    8GB (8192MB)	            8192 / 4.63 ≈ 1768 veces
    16GB (16384MB)	        16384 / 4.63 ≈ 3536 veces
    20GB (20480MB)	        20480 / 4.63 ≈ 4424 veces
"""

import os
import time
# Ruta al archivo base
input_file = '../../txt/words_lowercase_test_borrar.txt'

# Leemos el contenido base una sola vez
with open(input_file, 'r', encoding='utf-8') as f:
    base_content = f.read()

# Carpeta de salida (dos niveles arriba desde C, dentro de 'destino')
output_dir = os.path.abspath(os.path.join(__file__, "../../..", "txt"))
os.makedirs(output_dir, exist_ok=True)  # Crear si no existe
# print(f'Creando archivos en: {output_dir}')

# # Tamaños de destino en GB y sus repeticiones aproximadas
targets = {
    # '100MB.txt': 22, # 0.5 segundos
    '500MB_test.txt': 111, 
    # '1GB.txt': 221, # 13 segundos
    # '2GB.txt': 443, #12 segundos
    # '4GB.txt': 884, #57 segundos
    # '8GB.txt': 1768, # 157 segundos
    # '16GB.txt': 3536,  # 312 segundos
    # '20GB.txt': 4424    #  237 segundos
}

# Generar los archivos en la carpeta destino
for filename, repetitions in targets.items():
    output_path = os.path.join(output_dir, filename)
    start_time = time.time()
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for _ in range(repetitions):
            outfile.write(base_content)
    
    end_time = time.time()
    elapsed = end_time - start_time

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    # print(f'{filename} generado en {output_path} (~{size_mb:.2f} MB)')
    print(f'✅ {filename} generado en {output_path} (~{size_mb:.2f} MB) en {elapsed:.2f} segundos\n')

