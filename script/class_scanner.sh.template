#!/bin/bash

# local variable
CWD="/home/dnlab/WorkLogger"
WLAN=""

# check variable
if [ -z ${CWD} ]
then
    echo "CWD is not setted!"
    exit 0
fi
if [ -z ${WLAN} ]
then
    echo "WLAN is not setted!"
    exit 0
fi

# change wlan interface to monitor mode
ifconfig ${WLAN} down
iwconfig ${WLAN} mode monitor
ifconfig ${WLAN} up

# start scan
cd ${CWD}
source ./bin/activate
cd ./src/classscanner
python3 class_scanner.py

