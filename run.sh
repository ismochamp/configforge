#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
compiler="${CXX:-c++}"
"$compiler" -std=c++17 -O2 -Wall -Wextra -Wpedantic src/main.cpp -o build/migrator
exec python3 server.py "$@"
