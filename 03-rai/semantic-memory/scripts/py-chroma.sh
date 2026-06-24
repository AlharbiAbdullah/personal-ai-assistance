#!/usr/bin/env bash
# py-chroma.sh - Run a python script or inline python with chromadb available.
#
# System python3 (Arch, 3.14.x) has no chromadb module. This wrapper uses
# uv to run an ephemeral python 3.12 env with chromadb installed, cached
# in ~/.cache/uv so repeat invocations are fast.
#
# Usage:
#   py-chroma.sh /path/to/script.py [args...]
#   py-chroma.sh -c "import chromadb; ..."
#
# Why Python 3.12: chromadb wheels are published for 3.12, not yet 3.14.
set -euo pipefail
exec uv run --quiet --python 3.12 --with chromadb python3 "$@"
