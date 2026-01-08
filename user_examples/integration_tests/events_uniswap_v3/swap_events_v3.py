# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../"))

# Import scripts
from parsers.uniswap_v3 import parse_uni_v3_events
from shared import general_helpers
from shared import uniswap_v3_parsing
from shared import constants

# Test transaction
tx_hash = "0xf16f579a54c0d5700310ca54948d315b65b3f7d224a4af621ebfbaf29fcae8d5"
tx_hash = "0xd216e3c2ffdb0776a516b0074567618134b23ba021f700fbb4212b61435a3910"

# Uniswap v3 swap event
UNISWAP_V3_SWAP_EVENT = constants.UNISWAP_V3_SWAP_EVENT

# Get data
tx_data = general_helpers.get_tx_data_by_hash(tx_hash)
receipt_data = general_helpers.get_receipt_data_by_hash(tx_hash)

# Parse swap event
logs = receipt_data["logs"]
topics_0 = general_helpers.get_topics_0(logs)
swap_indexes = general_helpers.get_event_index(topics_0, UNISWAP_V3_SWAP_EVENT)

# check for swap events
pprint(uniswap_v3_parsing.has_UNISWAP_V3_SWAP_EVENT(topics_0))

# Load ABIs
PATH_UNISWAP_V3_PAIR_ABI = constants.PATH_UNISWAP_V3_PAIR_ABI
uniswap_v3_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V3_PAIR_ABI)

erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)

trades = parse_uni_v3_events.parse_v3_trades(
    logs, swap_indexes, erc20_abi, uniswap_v3_pair_abi
)
for trade in trades:
    pprint(
        "--------------------------------------------------------------------------------------"
    )
    # pprint(swap_log)
    pprint("Swap meta data:")
    pprint("DEX: {}".format(trade[0]))
    pprint("symbol0: {}".format(trade[1]))
    pprint("symbol1: {}".format(trade[2]))
    pprint("Decimals token0: {}".format(trade[3]))
    pprint("Decimals token1: {}".format(trade[4]))
    pprint("amount0: {}".format(trade[5]))
    pprint("amount1: {}".format(trade[6]))
    pprint("liquidity: {}".format(trade[7]))
    pprint("tick: {}".format(trade[8]))
    pprint("sqrt_price_x96: {}".format(trade[9]))
    pprint("price: {}".format(trade[10]))
    pprint(
        "--------------------------------------------------------------------------------------"
    )
