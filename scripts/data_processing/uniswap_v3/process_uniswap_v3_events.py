# Import packages
import time

start = time.time()
import argparse
import sys
import os
import multiprocessing
import logging
import pandas as pd
from pprint import pprint


# Import scripts
from dexamine.shared import general_helpers
from dexamine.shared import constants
from dexamine.parsers import uniswap_v3_parser

########################################################################################
# Parse Arguments Passed to the Script
########################################################################################

# Initialize argument parser
parser = argparse.ArgumentParser(description="Parse DEX events.")
parser.add_argument("input_file_json", help="Path to the input JSON file")
parser.add_argument("output_file_parquet", help="Path to the output PARQUET file")
parser.add_argument("log_file", help="Path to the log file")
parser.add_argument("contract_address", help="Pool smart contract address")

# Parse arguments
args = parser.parse_args()

# Paths from arguments
input_file_json = args.input_file_json
output_file_parquet = args.output_file_parquet
log_file = args.log_file
contract_address = args.contract_address  # Used on line 109

# Check that the input path exists
if not os.path.exists(os.path.dirname(input_file_json)):
    logger.error("input_file_json directory does not exist.")
    sys.exit(1)

# Check that the output path exists
if not os.path.exists(os.path.dirname(output_file_parquet)):
    logger.error("output_file_parquet directory does not exist.")
    sys.exit(1)


########################################################################################
# Set up logger
########################################################################################
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    filemode="w+",
)

logger = logging.getLogger(__name__)

# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
data = general_helpers.load_json(input_file_json)

# Flatten the dict into a list of tuples
block_index_pairs = [
    (block, index) for block, indexes in data.items() for index in indexes
]

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
erc20_bytes32_abi = general_helpers.load_abi(constants.PATH_ERC20_BYTES_ABI)
uniswap_v3_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V3_PAIR_ABI)

###################################################################################################
# Prepare arguments for multiprocessing
###################################################################################################
args_for_multiprocessing = [
    (block, index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi)
    for block, index in block_index_pairs
]


###################################################################################################
# Def multiprocess function
#
# Values from the tx:
# dict_keys(['blockHash', 'blockNumber', 'from', 'gas', 'gasPrice', 'maxPriorityFeePerGas',
# 'maxFeePerGas', 'hash', 'input', 'nonce', 'to', 'transactionIndex', 'value', 'type',
# 'accessList', 'chainId', 'v', 'r', 's'])
###################################################################################################
def parse_transaction(
    block_number, index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
):
    events = None  # Initialize events to None

    try:
        tx_data, receipt_data, block_data = (
            general_helpers.get_tx_receipt_block_by_index(
                hex(int(block_number)), hex(int(index))
            )
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect events
    try:
        logs = receipt_data["logs"]
        events = uniswap_v3_parser.parse_all_v3_events(
            logs,
            erc20_abi=erc20_abi,
            erc20_bytes32_abi=erc20_bytes32_abi,
            uniswap_v3_pair_abi=uniswap_v3_pair_abi,
            exchange_pair_address=contract_address,
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Return function if there are no Uniswap v3 events
    if events is None:
        return

    # Collect meta data
    try:
        hash = tx_data["hash"]
        to_address = tx_data["to"]

        # to_address is None if it's a contract creating transactions
        if to_address is None:
            to_address = "contract_creation"

        timestamp = block_data["timestamp"]
        timestamp = int(timestamp, 0)  # from hex to int

        from_address = tx_data["from"]
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

    # Identify type of transaction (direct to Uniswap router vs other)
    try:
        to_type = general_helpers.parse_to_type(to_address)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Append txes to global list
    try:
        for event in events:
            amount = event["amount"]
            amount_0 = event["amount_0"]
            amount_1 = event["amount_1"]
            decimals_0 = event["decimals_0"]
            decimals_1 = event["decimals_1"]
            dex_symbol = event["dex_symbol"]
            event_type = event["event_type"]
            owner = event["owner"]
            price = event["price"]
            recipient = event["recipient"]
            sender = event["sender"]
            sqrt_price_x96 = event["sqrt_price_x96"]
            symbol_0 = event["symbol_0"]
            symbol_1 = event["symbol_1"]
            tick = event["tick"]
            tick_lower = event["tick_lower"]
            tick_upper = event["tick_upper"]
            virtual_liquidity = event["virtual_liquidity"]
            virtual_reserve_0 = event["virtual_reserve_0"]
            virtual_reserve_1 = event["virtual_reserve_1"]

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
                event_type,
                dex_symbol,
                symbol_0,
                symbol_1,
                decimals_0,
                decimals_1,
                sender,
                recipient,
                owner,
                amount,
                amount_0,
                amount_1,
                virtual_liquidity,
                tick,
                sqrt_price_x96,
                price,
                tick_lower,
                tick_upper,
                virtual_reserve_0,
                virtual_reserve_1,
                to_type,
            ]
            L.append(data)
    except Exception as e:
        logger.error(e, exc_info=True)


###################################################################################################
# Collect transactions with the multiprocessing library
###################################################################################################
with multiprocessing.Manager() as manager:
    L = manager.list()  # Can be shared between multiprocesses
    n_cpu = multiprocessing.cpu_count()  # n threads
    # Processes outside of the loop otherwise too many files error
    # I've previously had trouble with too high maxtasksperchild and set it to 2, however, ChatGPT
    # thinks I can increase it a bit. So I should try it out for increased performance. Increasing
    # it from 2 to 15, made the test code run at 0.8s instead of 2.04. However, increating to 40
    # did not improve the speed further.
    pool = multiprocessing.Pool(n_cpu, maxtasksperchild=100)

    # Map get_tx to a range of blocks
    # pool.imap_unordered(parse_transaction, hashes_list)
    pool.starmap(parse_transaction, args_for_multiprocessing)

    pool.close()
    pool.join()  # Synchronization point needed for this to work
    transaction_data = list(L)

# pprint(transaction_data)

###################################################################################################
# Create Dataframe
###################################################################################################
# Transform to dataframe
col_names = [
    "timestamp",
    "block_number",
    "index",
    "hash",
    "from_address",
    "to_address",
    "value",
    "gas",
    "gasPrice",
    "maxPriorityFeePerGas",
    "maxFeePerGas",
    "event_type",
    "dex_symbol",
    "symbol_0",
    "symbol_1",
    "decimals_0",
    "decimals_1",
    "sender",
    "recipient",
    "owner",
    "amount",
    "amount_0",
    "amount_1",
    "virtual_liquidity",
    "tick",
    "sqrt_price_x96",
    "price",
    "tick_lower",
    "tick_upper",
    "virtual_reserve_0",
    "virtual_reserve_1",
    "to_type",
]

df = pd.DataFrame(data=transaction_data, columns=col_names)

# Sort dataframe by blockNumber
df = df.sort_values(by=["block_number", "index"])
pprint(df)

# Set the display option to show the full content of the column
# pd.set_option('display.max_colwidth', None)
# pprint(df[df['to_type']=='defi']['hash'])

###################################################################################################
# Write to file
###################################################################################################
# Define column types
column_types = {
    "timestamp": "Int64",  # Changed to nullable integer type
    "block_number": "Int64",  # Changed to nullable integer type
    "index": "Int64",  # Changed to nullable integer type
    "hash": "str",
    "from_address": "str",
    "to_address": "str",
    "value": "float64",
    "gas": "float64",
    "gasPrice": "float64",
    "maxPriorityFeePerGas": "float64",
    "maxFeePerGas": "float64",
    "event_type": "str",
    "dex_symbol": "str",
    "symbol_0": "str",
    "symbol_1": "str",
    "decimals_0": "Int64",  # Changed to nullable integer type
    "decimals_1": "Int64",  # Changed to nullable integer type
    "sender": "str",
    "recipient": "str",
    "owner": "str",
    "amount": "float64",
    "amount_0": "float64",
    "amount_1": "float64",
    "virtual_liquidity": "float64",
    "tick": "Int64",  # Changed to nullable integer type
    "sqrt_price_x96": "float64",
    "price": "float64",
    "tick_lower": "Int64",  # Changed to nullable integer type
    "tick_upper": "Int64",  # Changed to nullable integer type
    "virtual_reserve_0": "float64",
    "virtual_reserve_1": "float64",
    "to_type": "str",
}

# Apply types to DataFrame
for column, dtype in column_types.items():
    df[column] = df[column].astype(dtype)

# Now, df is ready to be saved as a Parquet file
df.to_parquet(output_file_parquet, index=False)

###################################################################################################
# Print elapsed time with days included
###################################################################################################
end = time.time()
elapsed_seconds = int(end - start)
days, rem = divmod(elapsed_seconds, 86400)
hours, rem = divmod(rem, 3600)
minutes, seconds = divmod(rem, 60)
pprint(
    "Elapsed time: {} days, {:0>2}:{:0>2}:{:0>2}".format(days, hours, minutes, seconds)
)
