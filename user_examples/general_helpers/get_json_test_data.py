# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
#sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from ethereum_defi_parser.shared import general_helpers

data = general_helpers.get_json_test_data("uniswap_v2/uniswap_v2_by_positions.json")

pprint(data)

abi = general_helpers.get_json_abi("uniswap_v2/IUniswapV2Pair.json")

pprint(abi)

tx = general_helpers.get_json_test_data("node_responses/tx_data.json")

pprint(tx)

