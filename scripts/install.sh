#!/bin/bash

ROOT_DIR=$(cd ../ && pwd)

python3 -m venv "$ROOT_DIR"/env

"$ROOT_DIR"/env/bin/pip install -r "$ROOT_DIR"/requirements.txt

"$ROOT_DIR"/env/bin/python3 "$ROOT_DIR"/manage.py makemigrations
"$ROOT_DIR"/env/bin/python3 "$ROOT_DIR"/manage.py migrate
"$ROOT_DIR"/env/bin/python3 "$ROOT_DIR"/manage.py loaddata "$ROOT_DIR"/initial_interval_data.json
