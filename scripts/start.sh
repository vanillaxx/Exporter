#!/bin/bash

ROOT_DIR=$(cd ../ && pwd)

if [ ! -d "$ROOT_DIR"/exporter ]; then 
	. ./install.sh
fi

"$ROOT_DIR"/exporter/bin/python3 "$ROOT_DIR"/manage.py runserver
