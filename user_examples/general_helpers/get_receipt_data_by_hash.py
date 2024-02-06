# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from ethereum_defi_parser.shared import general_helpers, constants

tx_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"

receipt_data = general_helpers.get_receipt_data_by_hash(tx_hash)

pprint(receipt_data)
