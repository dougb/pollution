#!/bin/sh

NUM_FILES=1

while [ -e data.json.${NUM_FILES}.gz ]; do
    NUM_FILES=`expr $NUM_FILES + 1`
done

echo "NumFiles:$NUM_FILES"

while [ $NUM_FILES -gt 0 ];do
    PREV_FILE=`expr $NUM_FILES - 1`
    mv data.json.${PREV_FILE}.gz data.json.${NUM_FILES}.gz
    NUM_FILES=$PREV_FILE
done

if [ -e data.json.0.gz ]; then
    echo ERROR, logic problem.
else
    gzip -9c data.json > data.json.0.gz
    cp /dev/null data.json
fi


