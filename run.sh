#!/bin/sh

mkdir -p /tmp/mx

while [ 1 ]; do
    ./mixing_height.py
    date
    sleep 3600
done
