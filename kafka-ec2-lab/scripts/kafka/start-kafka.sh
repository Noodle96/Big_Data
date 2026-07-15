#!/usr/bin/env bash

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: Ejecuta este script con sudo."
    exit 1
fi

systemctl start kafka

sleep 3

systemctl --no-pager --full status kafka
