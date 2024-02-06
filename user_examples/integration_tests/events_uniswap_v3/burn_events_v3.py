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
UNISWAP_V3_BURN_EVENT = constants.UNISWAP_V3_BURN_EVENT

# Get data
tx_data = general_helpers.get_tx_data_by_hash(tx_hash)
receipt_data = general_helpers.get_receipt_data_by_hash(tx_hash)

# Parse swap event
logs = receipt_data['logs']
topics_0 = general_helpers.get_topics_0(logs)
burn_indexes = general_helpers.get_event_index(topics_0, UNISWAP_V3_BURN_EVENT)

# check for swap events
pprint(uniswap_v3_parsing.has_uniswap_v3_burn_event(topics_0))

# Load ABIs
PATH_UNISWAP_V3_PAIR_ABI = constants.PATH_UNISWAP_V3_PAIR_ABI
uniswap_v3_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V3_PAIR_ABI)

erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)

burns = parse_uni_v3_events.parse_v3_burns(logs, burn_indexes, erc20_abi, uniswap_v3_pair_abi)

pprint(burns)
