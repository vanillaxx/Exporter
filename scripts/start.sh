#!/bin/bash

ROOT_DIR=$(cd ../ && pwd)

if [ ! -d "$ROOT_DIR"/env ]; then 
	. ./install.sh
fi

cd ../ && "$ROOT_DIR"/env/bin/python3 "$ROOT_DIR"/manage.py runserver
