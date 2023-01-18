#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
    echo "go away by default"

    kill $http_server

    exit 0
}

python3 -m http.server --directory /boot/bydefault/web/ & http_server=$!
# python3 -u travel.py
chromium --enable-logging=stderr --start-fullscreen  --noerrdialogs --disable-translate --no-first-run --disable-infobars --window-position=0,0 --window-size=1920,1100 http://localhost:8000/?targets=%5B%5B%5B39%2C104%5D%2C%5B30%2C900%5D%2C%5B838%2C115%5D%2C%5B818%2C891%5D%5D%2C%5B%5B527%2C564%5D%2C%5B525%2C685%5D%2C%5B627%2C564%5D%2C%5B625%2C680%5D%5D%2C%5B%5B312%2C144%5D%2C%5B306%2C390.984375%5D%2C%5B667%2C146%5D%2C%5B663%2C392%5D%5D%2C%5B%5B101%2C446%5D%2C%5B100%2C571%5D%2C%5B243%2C445%5D%2C%5B240%2C569%5D%5D%2C%5B%5B132%2C684%5D%2C%5B132%2C796%5D%2C%5B385%2C679%5D%2C%5B382%2C793%5D%5D%2C%5B%5B673%2C449%5D%2C%5B671%2C623%5D%2C%5B797%2C448%5D%2C%5B792%2C622%5D%5D%2C%5B%5B705%2C188%5D%2C%5B702%2C320%5D%2C%5B828%2C191%5D%2C%5B822%2C319%5D%5D%2C%5B%5B81%2C207%5D%2C%5B82%2C331%5D%2C%5B264%2C206%5D%2C%5B261%2C335%5D%5D%2C%5B%5B310%2C465%5D%2C%5B310%2C589%5D%2C%5B492%2C467%5D%2C%5B488%2C589%5D%5D%5D