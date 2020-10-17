#!/bin/bash

ROOT_DIR=$(cd ../ && pwd)

python3 -m venv "$ROOT_DIR"/exporter

"$ROOT_DIR"/exporter/bin/pip install -r "$ROOT_DIR"/requirements.txt
