#!/bin/bash

trap ctrl_c INT

list_descendants () {
  local children=$(ps -o pid= --ppid "$1")

  for pid in $children; do
    list_descendants "$pid"
  done

  echo "$children"
}

function ctrl_c() {
    echo "go away by default"

    kill -15 http_server

    exit 0
}

python3 -m http.server --directory /boot/bydefault/web/ & http_server=$!
python3 -u travel.py