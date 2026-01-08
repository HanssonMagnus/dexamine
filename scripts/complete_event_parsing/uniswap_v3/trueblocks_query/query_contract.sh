#!/bin/bash

# Check if contract address and output file path are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <contract_address> <output_file>"
    exit 1
fi

# Assign arguments to variables
CONTRACT_ADDRESS=$1
OUTPUT_FILE=$2

# Command to query the Ethereum node using TrueBlocks
# Output format is CSV with blockNumber and transactionIndex
{
    echo 'blockNumber,transactionIndex'
    chifra list $CONTRACT_ADDRESS | awk '(NR>1) {print $2","$3}' #"," for csv format
} > $OUTPUT_FILE
