"""
Load a chifra-list, e.g., "txes_eth_usdc.csv", and parse it into .json format in the
same fashion as the "eth_arbs" project. I.e., the block is the key, and the values are
all txes in that block.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import argparse
import os
import sys
import csv
import json
import logging
from importlib import resources

# Import modules
from dexamine.shared import general_helpers

# Initialize argument parser
parser = argparse.ArgumentParser(description='Process chifra transaction data.')
parser.add_argument('input_path', help='Path to the input CSV file')
parser.add_argument('output_path', help='Path to the output JSON file')
parser.add_argument('log_path', help='Path to the log directory (same as files)')

# Parse arguments
args = parser.parse_args()

# Paths from arguments
path_input = args.input_path
path_output = args.output_path
path_log = args.log_path

# Set up logger
logging.basicConfig(filename=path_log, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

# Create json/dict of transactions
try:
    with open(path_input, mode='r', encoding='utf-8') as file:
        csv_content = file.read()
    tx_dict = general_helpers.chifra_csv_to_json(csv_content)

except Exception as e:
    logger.error(e, exc_info=True)

# Save dictionary as JSON
with open(path_output, 'w+') as fjson:
    json.dump(tx_dict, fjson, indent=4)
fjson.close()
