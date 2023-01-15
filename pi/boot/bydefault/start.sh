#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
    echo "go away by default"

    kill $http_server

    exit 0
}

python3 -m http.server --directory /boot/bydefault/web/ & http_server=$!
python3 -u travel.py

# chromium --enable-logging=stderr --start-fullscreen  --noerrdialogs --disable-translate --no-first-run --disable-infobars --window-position=0,0 --window-size=1920,1100