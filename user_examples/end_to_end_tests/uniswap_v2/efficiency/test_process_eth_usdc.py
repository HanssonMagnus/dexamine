# Import packages
import sys
import os
import cProfile
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../../"))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v2 import parse_uni_v2_events

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = "tests/eth_usdc_efficiency.log"
logging.basicConfig(
    filename=PATH_LOGS + log_name,
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    filemode="w+",
)
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data
PATH_UNISWAP_V2_BY_POSITIONS = constants.PATH_UNISWAP_V2_BY_POSITIONS

# Full data set

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
data = general_helpers.load_json(PATH_UNISWAP_V2_BY_POSITIONS)

# Flatten the dict into a list of tuples
block_index_pairs = [
    (block, index) for block, indexes in data.items() for index in indexes
]

# Smart contract address of USDC-WETH pool
UNISWAP_V2_USDC_WETH_ADDRESS = constants.UNISWAP_V2_USDC_WETH_ADDRESS


###################################################################################################
# Def multiprocess function
#
# Values from the tx:
# dict_keys(['blockHash', 'blockNumber', 'from', 'gas', 'gasPrice', 'maxPriorityFeePerGas',
# 'maxFeePerGas', 'hash', 'input', 'nonce', 'to', 'transactionIndex', 'value', 'type',
# 'accessList', 'chainId', 'v', 'r', 's'])
###################################################################################################
def parse_transaction(block_number, index):
    try:
        tx_data, receipt_data, block_data = (
            general_helpers.get_tx_receipt_block_by_index(
                hex(int(block_number)), hex(int(index))
            )
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect meta data
    try:
        timestamp = block_data["timestamp"]
        timestamp = int(timestamp, 0)  # from hex to int
        hash = tx_data["hash"]
        from_address = tx_data["from"]
        to_address = tx_data["to"]
        tx_type = int(tx_data["type"], 16)

        value = int(tx_data["value"], 16)
        gas = int(tx_data["gas"], 16)
        gasPrice = int(tx_data["gasPrice"], 16)

        if int(tx_data["type"], 16) == 2:  # EIP-1559 (type 2) transactions
            maxPriorityFeePerGas = int(tx_data["maxPriorityFeePerGas"], 16)
            maxFeePerGas = int(tx_data["maxFeePerGas"], 16)
        else:  # Legacy (type 0) and EIP-2930 (type 1) transactions
            maxPriorityFeePerGas = 0
            maxFeePerGas = 0

    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect events
    try:
        logs = receipt_data["logs"]
        events = parse_uni_v2_events.parse_all_v2_events(
            logs, exchange_pair_address=UNISWAP_V2_USDC_WETH_ADDRESS
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Append txes to global list
    try:
        for event in events:
            type_of_event = event[0]
            dex_symbol = event[1]
            symbol_0 = event[2]
            symbol_1 = event[3]
            decimals_0 = event[4]
            decimals_1 = event[5]
            dxt = event[6]
            dyt = event[7]
            xt1 = event[8]
            yt1 = event[9]
            pt1 = event[10]
            kt1 = event[11]
            data = [
                timestamp,
                block_number,
                index,
                hash,
                from_address,
                to_address,
                value,
                gas,
                gasPrice,
                maxPriorityFeePerGas,
                maxFeePerGas,
                type_of_event,
                dex_symbol,
                symbol_0,
                symbol_1,
                decimals_0,
                decimals_1,
                dxt,
                dyt,
                xt1,
                yt1,
                pt1,
                kt1,
            ]
            # L.append(data)
            print(data)
    except Exception as e:
        logger.error(e, exc_info=True)


###################################################################################################
# Collect transactions with the multiprocessing library
###################################################################################################
block_index_pair = block_index_pairs[-1]
pprint(block_index_pair)
cProfile.run("parse_transaction(block_index_pair[0], block_index_pair[1])")
