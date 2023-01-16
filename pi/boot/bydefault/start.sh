#!/bin/bash

trap ctrl_c INT

function ctrl_c() {
    echo "go away by default"

    kill $http_server

    exit 0
}

python3 -m http.server --directory /boot/bydefault/web/ & http_server=$!
# python3 -u travel.py
chromium --enable-logging=stderr --start-fullscreen  --noerrdialogs --disable-translate --no-first-run --disable-infobars --window-position=0,0 --window-size=1920,1100 http://localhost:8000/?targets=%5B%5B%5B37%2C113%5D%2C%5B20%2C906%5D%2C%5B833%2C123%5D%2C%5B813%2C899%5D%5D%2C%5B%5B465%2C447%5D%2C%5B502%2C572%5D%2C%5B587%2C454%5D%2C%5B583%2C570%5D%5D%2C%5B%5B304%2C146%5D%2C%5B298%2C323.984375%5D%2C%5B559%2C146%5D%2C%5B554%2C324%5D%5D%2C%5B%5B43%2C183.00000286102295%5D%2C%5B52%2C285.00000762939453%5D%2C%5B225%2C191.00000298023224%5D%2C%5B223%2C290.00000762939453%5D%5D%2C%5B%5B76%2C643%5D%2C%5B104%2C823%5D%2C%5B474%2C680%5D%2C%5B478%2C832%5D%5D%2C%5B%5B898%2C285%5D%2C%5B903%2C497%5D%2C%5B982%2C284%5D%2C%5B1022%2C494%5D%5D%2C%5B%5B912%2C128%5D%2C%5B929%2C215%5D%2C%5B1064%2C140%5D%2C%5B1072%2C219%5D%5D%2C%5B%5B86%2C5%5D%2C%5B74%2C71%5D%2C%5B322%2C8%5D%2C%5B317%2C77%5D%5D%2C%5B%5B160%2C400%5D%2C%5B155%2C550%5D%2C%5B311%2C414%5D%2C%5B329%2C489%5D%5D%5D