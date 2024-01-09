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

###################################################################################################
# Import test data
###################################################################################################
path_uni_v3_by_positions = constants.path_uni_v3_by_positions
data = general_helpers.load_json(path_uni_v3_by_positions)

blocks = list(data.keys())

# Parse transations
#blocks = blocks[83:84] # test with only 1 tx (2 swaps)
blocks = blocks[0:1] # test with only 1 tx (2 swaps)
for block in blocks:
    tx_indexes = data[block]
    for index in tx_indexes:
        # Get transaction data
        try:
            tx_data, receipt_data, block_data = general_helpers.get_tx_receipt_block_by_index(hex(int(block)),
                                                                                hex(int(index)))
        except Exception as e:
            logger.error(e, exc_info=True)

#pprint(tx_data)
#pprint(receipt_data)
###################################################################################################
# Parse Mints
###################################################################################################
# Uniswap v3 mint event
uniswap_v3_mint_event = constants.uniswap_v3_mint_event

# Parse mint event
logs = receipt_data['logs']
topics_0 = general_helpers.get_topics_0(logs)
mint_indexes = general_helpers.get_event_index(topics_0, uniswap_v3_mint_event)

# Check for mint events
pprint(uniswap_v3_parsing.has_uniswap_v3_mint_event(topics_0))

# Load ABIs
path_uniswap_v3_pair_abi = constants.path_uniswap_v3_pair_abi
uniswap_v3_pair_abi = general_helpers.load_abi(constants.path_uniswap_v3_pair_abi)

path_erc20_abi = constants.path_erc20_abi
erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)

mints = parse_uni_v3_events.parse_v3_mints(logs, mint_indexes, erc20_abi, uniswap_v3_pair_abi)
pprint(mints)

#trades = parse_uni_v3_events.parse_v3_trades(logs, swap_indexes, erc20_abi, uniswap_v3_pair_abi)
#for trade in trades:
#    pprint("--------------------------------------------------------------------------------------")
#    #pprint(swap_log)
#    pprint("Swap meta data:")
#    pprint("DEX: {}".format(trade[0]))
#    pprint("symbol0: {}".format(trade[1]))
#    pprint("symbol1: {}".format(trade[2]))
#    pprint("Decimals token0: {}".format(trade[3]))
#    pprint("Decimals token1: {}".format(trade[4]))
#    pprint("amount0: {}".format(trade[5]))
#    pprint("amount1: {}".format(trade[6]))
#    pprint("liquidity: {}".format(trade[7]))
#    pprint("tick: {}".format(trade[8]))
#    pprint("sqrtPriceX96: {}".format(trade[9]))
#    pprint("price: {}".format(trade[10]))
#    pprint("--------------------------------------------------------------------------------------")
