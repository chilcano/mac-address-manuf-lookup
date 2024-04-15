#!/bin/bash

# Start the first process
python mac_manuf_api_rest.py &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start mac_manuf_api_rest.py: $status"
  exit $status
fi

# Start the second process
python mac_manuf_api_rest_https.py &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start mac_manuf_api_rest_https.py: $status"
  exit $status
fi

while /bin/true; do
  PROCESS_1_STATUS=$(ps aux |grep -q mac_manuf_api_rest.py |grep -v grep)
  PROCESS_2_STATUS=$(ps aux |grep -q mac_manuf_api_rest_https.py | grep -v grep)
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit -1
  fi
  sleep 60
done
