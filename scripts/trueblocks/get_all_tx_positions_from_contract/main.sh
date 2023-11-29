#!/bin/bash

# Debug mode
#set -x

# Start timer and print start message
start_time="$(date -u +%s)"
echo 'The script is starting!'

# Default configuration file
CONFIG_FILE="default_config.cfg"

# Check if a custom config file is provided as an argument
if [ "$1" != "" ]; then
    CONFIG_FILE=$1
fi

# Source the configuration file
source $CONFIG_FILE

# Output path and contract address are set in the config file
echo "Querying contract: $CONTRACT_ADDRESS"
echo "The chifra csv will be saved at: $OUTPUT_FILE_CSV"
echo "The json will be saved at: $OUTPUT_FILE_JSON"

# Run chifra script
./query_contract.sh $CONTRACT_ADDRESS $OUTPUT_FILE_CSV

# Run the Python script that transforms the chifra csv to json
python csv_to_json.py $OUTPUT_FILE_CSV $OUTPUT_FILE_JSON

# Print time elapsed
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Elapsed time: $elapsed seconds."
