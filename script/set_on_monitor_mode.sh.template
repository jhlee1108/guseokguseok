#!/bin/bash

WLAN="wlx0013ef70600e"

if [ -z ${WLAN} ]
then
    echo "WLAN is not setted!"
    exit 0
fi

ifconfig ${WLAN} down
iwconfig ${WLAN} mode monitor
ifconfig ${WLAN} up
