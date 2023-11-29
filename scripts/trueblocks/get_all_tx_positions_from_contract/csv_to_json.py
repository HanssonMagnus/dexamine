# Load a chifra-list, e.g., "txes_eth_usdc.csv", and parse it into .json format
# in the same fashion as the "eth_arbs" project. I.e., the block is the key,
# and the values are all txes in that block.

# Import packages
import argparse
import os
import sys
import csv
import json

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../'))

# Import scirpts
from shared import general_helpers

# Initialize argument parser
parser = argparse.ArgumentParser(description='Process chifra transaction data.')
parser.add_argument('input_path', help='Path to the input CSV file')
parser.add_argument('output_path', help='Path to the output JSON file')

# Parse arguments
args = parser.parse_args()

# Paths from arguments
path_input = args.input_path
path_output = args.output_path

# Create json/dict of transactions
tx_dict = general_helpers.chifra_csv_to_json(path_input)

# Save dictionary as JSON
with open(path_output, 'w+') as fjson:
    json.dump(tx_dict, fjson, indent=4)
fjson.close()
