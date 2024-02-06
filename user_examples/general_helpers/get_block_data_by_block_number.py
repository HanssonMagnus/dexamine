# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from ethereum_defi_parser.shared import general_helpers, constants

block_number = "0xbcda99"

block_data = general_helpers.get_block_data_by_block_number(block_number)

pprint(block_data)
