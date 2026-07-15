#!/usr/bin/env bash

set -euo pipefail

echo "============================================================"
echo "Estado de Kafka en $(hostname)"
echo "============================================================"

systemctl --no-pager --full status kafka || true

echo
echo "Puertos Kafka:"
ss -lntp | grep -E ':9092|:9093' || true

echo
echo "Últimos logs:"
journalctl \
    --unit kafka \
    --no-pager \
    --lines 30
