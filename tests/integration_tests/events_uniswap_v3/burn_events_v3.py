# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../'))

# Import scripts
from parsers.uniswap_v3 import parse_uni_v3_events
from shared import general_helpers
from shared import uniswap_v3_parsing
from shared import constants

# Test transaction
tx_hash = '0x2073cca6126fdeb8a9e4bf413dcbb8770f2f0a08a54d95b16735ee2be269a68a'

# Uniswap v3 swap event
uniswap_v3_burn_event = constants.uniswap_v3_burn_event

# Get data
tx_data = general_helpers.get_tx_data_by_hash(tx_hash)
receipt_data = general_helpers.get_receipt_data_by_hash(tx_hash)

# Parse swap event
logs = receipt_data['logs']
topics_0 = general_helpers.get_topics_0(logs)
burn_indexes = general_helpers.get_event_index(topics_0, uniswap_v3_burn_event)

# check for swap events
pprint(uniswap_v3_parsing.has_uniswap_v3_burn_event(topics_0))

# Load ABIs
path_uniswap_v3_pair_abi = constants.path_uniswap_v3_pair_abi
uniswap_v3_pair_abi = general_helpers.load_abi(constants.path_uniswap_v3_pair_abi)

path_erc20_abi = constants.path_erc20_abi
erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)

burns = parse_uni_v3_events.parse_v3_burns(logs, burn_indexes, erc20_abi, uniswap_v3_pair_abi)

pprint(burns)
