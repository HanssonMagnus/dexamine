# Load a chifra-list, e.g., "txes_eth_usdc.csv", and parse it into .json format
# in the same fashion as the "eth_arbs" project. I.e., the block is the key,
# and the values are all txes in that block.
"""
This file contains a unit test for general_helpers.chifra_csv_to_json().

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import sys
import os
import json
from pprint import pprint
import importlib.resources as pkg_resources

# Set the path to the root of the project
# sys.path.append(os.path.abspath('../../../../'))

# Import scirpts
from dexamine.shared import constants, general_helpers

# Read in the chifra csv file
# path_input = constants.PATH_UNISWAP_V2_TEST_DATA_DIR + "uni_v2_by_positions.csv"

# Output the json file
# path_output = constants.PATH_UNISWAP_V2_BY_POSITIONS

csv_content = general_helpers.get_csv_test_data_as_string(
    "uniswap_v2/uniswap_v2_by_positions.csv"
)

# pprint(csv_content)
# Create json/dict of transactions
tx_dict = general_helpers.chifra_csv_to_json(csv_content)
pprint(tx_dict)

# Save dictionary as JSON
# with open(path_output, 'w+', encoding="utf-8") as fjson:
#    json.dump(tx_dict, fjson, indent=4)
# fjson.close()
