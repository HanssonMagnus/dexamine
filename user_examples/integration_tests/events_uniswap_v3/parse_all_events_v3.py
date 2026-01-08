# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../"))

# Import scripts
from dexamine.parsers import uniswap_v3_parser
from dexamine.shared import general_helpers
from dexamine.shared import uniswap_v3_parsing
from dexamine.shared import constants

########################################################################################
# Set up logger
########################################################################################
logger = logging.getLogger(__name__)

# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
erc20_bytes32_abi = general_helpers.load_abi(constants.PATH_ERC20_BYTES_ABI)
uniswap_v3_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V3_PAIR_ABI)

###################################################################################################
# Import test data
###################################################################################################
PATH_UNISWAP_V3_BY_POSITIONS = constants.PATH_UNISWAP_V3_BY_POSITIONS
data = general_helpers.load_json(PATH_UNISWAP_V3_BY_POSITIONS)

blocks = list(data.keys())

# Parse transations
# blocks = blocks[83:84] # test with only 1 tx (2 swaps)
# blocks = blocks[0:1] # test with only 1 tx (2 swaps)
for block in blocks:
    tx_indexes = data[block]
    for index in tx_indexes:
        # Get transaction data
        try:
            tx_data, receipt_data, block_data = (
                general_helpers.get_tx_receipt_block_by_index(
                    hex(int(block)), hex(int(index))
                )
            )
            # Get logs
            logs = receipt_data["logs"]

            # Parse all events
            events = uniswap_v3_parser.parse_all_v3_events(
                logs,
                erc20_abi=erc20_abi,
                erc20_bytes32_abi=erc20_bytes32_abi,
                uniswap_v3_pair_abi=uniswap_v3_pair_abi,
                exchange_pair_address="",
            )
            pprint(events)

        except Exception as e:
            logger.error(e, exc_info=True)

# pprint(tx_data)
# pprint(receipt_data)
###################################################################################################
# Parse Mints
###################################################################################################
# Uniswap v3 mint event
# UNISWAP_V3_MINT_EVENT = constants.UNISWAP_V3_MINT_EVENT

# trades = parse_uni_v3_events.parse_v3_trades(logs, swap_indexes, erc20_abi, uniswap_v3_pair_abi)
# for trade in trades:
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
#    pprint("sqrt_price_x96: {}".format(trade[9]))
#    pprint("price: {}".format(trade[10]))
#    pprint("--------------------------------------------------------------------------------------")
