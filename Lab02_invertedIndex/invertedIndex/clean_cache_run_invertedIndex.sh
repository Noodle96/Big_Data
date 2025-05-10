#!/bin/bash

# Verificamos que se estemos ejecutando como root
if [[ $EUID -ne 0 ]]; then
   echo "Este script debe ejecutarse con sudo."
   exit 1
fi

# Limpiando caché
echo "[INFO] Sincronizando disco y limpiando caché..."
sync
echo 3 > /proc/sys/vm/drop_caches

# Ejecuta el programa
echo "[INFO] Ejecutando invertedIndex..."
./invertedIndex
