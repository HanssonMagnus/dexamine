#!/bin/bash

# Debug mode
#set -x

# Start timer and print start message
start_time="$(date -u +%s)"
echo 'Ready your nets Dexamine is starting!'

# Set the configuration file as the first argument
CONFIG_FILE=$1

# Source the configuration file
source $CONFIG_FILE

# Ensure the directories for Trueblocks and Dexamine exist
mkdir -p "${BASE_DIR}/${TRUEBLOCKS_DIR}"
mkdir -p "${DEXAMINE_DIR}"

# Output path and contract address are set in the config file
echo "Querying contract: $CONTRACT_ADDRESS"
echo "The chifra csv will be saved at: $TRUEBLOCKS_OUTPUT_FILE_CSV"
echo "The json will be saved at: $TRUEBLOCKS_OUTPUT_FILE_JSON"
echo "The Python log will be saved at: $TRUEBLOCKS_LOG_FILE"

# Run chifra script
#./trueblocks_query/query_contract.sh $CONTRACT_ADDRESS $TRUEBLOCKS_OUTPUT_FILE_CSV
/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/trueblocks_query/query_contract.sh $CONTRACT_ADDRESS $TRUEBLOCKS_OUTPUT_FILE_CSV

# Run the Python script that transforms the chifra csv to json
#python ./trueblocks_query/csv_to_json.py $TRUEBLOCKS_OUTPUT_FILE_CSV $TRUEBLOCKS_OUTPUT_FILE_JSON $TRUEBLOCKS_LOG_FILE
python /home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/trueblocks_query/csv_to_json.py $TRUEBLOCKS_OUTPUT_FILE_CSV $TRUEBLOCKS_OUTPUT_FILE_JSON $TRUEBLOCKS_LOG_FILE

# Run the Python script for Dexamine parsing
#python ./dexamine_parsing/process_uniswap_v3_events.py $TRUEBLOCKS_OUTPUT_FILE_JSON $DEXAMINE_OUTPUT_FILE $DEXAMINE_LOG_FILE $CONTRACT_ADDRESS
python /home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/dexamine_parsing/process_uniswap_v3_events.py $TRUEBLOCKS_OUTPUT_FILE_JSON $DEXAMINE_OUTPUT_FILE $DEXAMINE_LOG_FILE $CONTRACT_ADDRESS

# Print time elapsed
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Elapsed time: $elapsed seconds."
