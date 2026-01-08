#!/bin/bash
# Script for parsing specific contract

########################################################################################
# Changeable Variable
########################################################################################
# Name of exchange pair
POOL_NAME="wbtc_weth_03"

# Set the contract address
CONTRACT_ADDRESS="0xCBCdF9626bC03E24f779434178A73a0B4bad62eD" # Uni v3 WBTC-WETH 0.3%
########################################################################################


########################################################################################
# Paths to directories
########################################################################################
# Trueblocks file of positions
DIR_TRUEBLOCKS="/media/m2_front/research/data/trueblocks_lists/uniswap_v3"
INPUT_FILE_NAME="${POOL_NAME}/2024-02-13_${POOL_NAME}_positions.json"

INPUT_FILE_JSON="${DIR_TRUEBLOCKS}/${INPUT_FILE_NAME}"

# Output file
DIR_DEXAMINE="/media/m2_front/research/data/projects/dexamine/uniswap_v3"
OUTPUT_FILE_NAME="${POOL_NAME}/events_${POOL_NAME}.parquet"

OUTPUT_FILE_PARQUET="${DIR_DEXAMINE}/${OUTPUT_FILE_NAME}"

# Log file
LOG_FILE_NAME="${DIR_DEXAMINE}/${POOL_NAME}/${POOL_NAME}.log"

########################################################################################
# Run parser
########################################################################################
# Run the Python script that transforms the chifra csv to json
python ../process_uniswap_v3_events.py $INPUT_FILE_JSON $OUTPUT_FILE_PARQUET $LOG_FILE_NAME $CONTRACT_ADDRESS
