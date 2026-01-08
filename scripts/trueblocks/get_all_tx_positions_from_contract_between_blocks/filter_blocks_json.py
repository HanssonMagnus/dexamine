# Load a json chifra-list where the block is the key and the values are all txes in that block.
# Output a similar json file that is restricted to between start_block and end_block.

# Import packages
import os
import sys
import csv
import json

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../"))

# Import scirpts
from shared import general_helpers

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Blocks
block_start = 18251965  # 2023-10-01
block_end = 18473542  # 2023-10-31
block_end = 18273436  # 2023-10-03

# File pahts
dir_path = "/media/m2_front/research/data/trueblocks_lists/uniswap_v3/"
file_in = dir_path + "2023-11-23_eth_usdc_05_positions.json"
file_out = dir_path + "2023-11-23_eth_usdc_05_positions_october.json"
file_out = dir_path + "2023-11-23_eth_usdc_05_positions_october_test.json"

###################################################################################################
# Filter blocks
###################################################################################################
general_helpers.filter_blocks(file_in, file_out, block_start, block_end)
