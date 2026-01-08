"""
This is a user script that runs the Uniswap v2 parser with a set of argument.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import time
import argparse
import sys
import os
import multiprocessing
import logging
from pprint import pprint
import pandas as pd

# Import scripts
from dexamine.shared import general_helpers
from dexamine.shared import constants
from dexamine.parsers import uniswap_v2_parser

# Start timer
start = time.time()

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

########################################################################################
# Check that the input path exists
########################################################################################
if not os.path.exists(os.path.dirname(input_file_json)):
    logger.error("input_file_json directory does not exist.")
    sys.exit(1)

# Check that the output path exists
if not os.path.exists(os.path.dirname(output_file_parquet)):
    logger.error("output_file_parquet directory does not exist.")
    sys.exit(1)

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
tx_json_data = general_helpers.load_json(input_file_json)

# Flatten the dict into a list of tuples
block_index_pairs = [
    (block, index) for block, indexes in tx_json_data.items() for index in indexes
]

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
erc20_bytes32_abi = general_helpers.load_abi(constants.PATH_ERC20_BYTES_ABI)
uniswap_v2_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V2_PAIR_ABI)

###################################################################################################
# Load MEV contracts
###################################################################################################
mev_contracts = general_helpers.load_txt(
    constants.PATH_MEV_CONTRACTS
)  # Generator object
mev_contracts_list = list(mev_contracts)

###################################################################################################
# Prepare arguments for multiprocessing
###################################################################################################
args_for_multiprocessing = [
    (
        block,
        index,
        erc20_abi,
        erc20_bytes32_abi,
        uniswap_v2_pair_abi,
        mev_contracts_list,
    )
    for block, index in block_index_pairs
]


###################################################################################################
# Def multiprocess function
###################################################################################################
def parse_transaction(
    block_number_local,
    index_local,
    erc20_abi_local,
    erc20_bytes32_abi_local,
    uniswap_v2_pair_abi_local,
    mev_contracts_list_local,
):
    """Parse function for multiprocessing."""
    events = None  # Initialize events to None

    try:
        tx_data, receipt_data, block_data = (
            general_helpers.get_tx_receipt_block_by_index(
                hex(int(block_number_local)), hex(int(index_local))
            )
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect events
    try:
        logs = receipt_data["logs"]
        events = uniswap_v2_parser.parse_all_uniswap_v2_events(
            logs,
            erc20_abi=erc20_abi_local,
            erc20_bytes32_abi=erc20_bytes32_abi_local,
            uniswap_v2_pair_abi=uniswap_v2_pair_abi_local,
            exchange_pair_address=contract_address,
        )
    except Exception as e:
        logger.error(e, exc_info=True)

    # Return function if there are no Uniswap v2 events
    if events is None:
        return

    # Collect meta data
    try:
        tx_hash = tx_data["hash"]
        to_address = tx_data["to"]

        # THIS IS NOW IN general_helpers.parse_to_type
        # to_address is None if it's a contract creating transactions
        #if to_address is None:
        #    to_address = "contract_creation"

        timestamp = block_data["timestamp"]
        timestamp = int(timestamp, 0)  # from hex to int

        from_address = tx_data["from"]

        value = int(tx_data["value"], 16)
        gas = int(tx_data["gas"], 16)
        gas_price = int(tx_data["gasPrice"], 16)

        tx_type = int(tx_data["type"], 16)
        if tx_type == 2:  # EIP-1559 (type 2) transactions
            max_priority_fee_per_gas = int(tx_data["maxPriorityFeePerGas"], 16)
            max_fee_per_gas = int(tx_data["maxFeePerGas"], 16)
        else:  # Legacy (type 0) and EIP-2930 (type 1) transactions
            max_priority_fee_per_gas = 0
            max_fee_per_gas = 0

    except Exception as e:
        logger.error(e, exc_info=True)

    # Identify type of transaction (MEV, DeFi, UNI)
    try:
        to_type = general_helpers.parse_to_type(to_address, mev_contracts_list_local)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Append txes to global list
    try:
        for event in events:
            amount_0 = event["amount_0"]
            amount_0_in = event["amount_0_in"]
            amount_0_out = event["amount_0_out"]
            amount_1 = event["amount_1"]
            amount_1_in = event["amount_1_in"]
            amount_1_out = event["amount_1_out"]
            decimals_0 = event["decimals_0"]
            decimals_1 = event["decimals_1"]
            event_index = event["event_index"]
            dex_symbol = event["dex_symbol"]
            event_type = event["event_type"]
            invariant = event["invariant"]
            mid_price = event["mid_price"]
            reserve_0 = event["reserve_0"]
            reserve_1 = event["reserve_1"]
            symbol_0 = event["symbol_0"]
            symbol_1 = event["symbol_1"]

            data = [
                timestamp,
                block_number_local,
                index_local,
                event_index,
                tx_hash,
                from_address,
                to_address,
                value,
                gas,
                gas_price,
                max_priority_fee_per_gas,
                max_fee_per_gas,
                event_type,
                dex_symbol,
                symbol_0,
                symbol_1,
                decimals_0,
                decimals_1,
                amount_0,
                amount_1,
                amount_0_in,
                amount_0_out,
                amount_1_in,
                amount_1_out,
                reserve_0,
                reserve_1,
                mid_price,
                invariant,
                to_type,
                tx_type,
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
    "event_index",
    "tx_hash",
    "from_address",
    "to_address",
    "value",
    "gas",
    "gas_price",
    "max_priority_fee_per_gas",
    "max_fee_per_gas",
    "event_type",
    "dex_symbol",
    "symbol_0",
    "symbol_1",
    "decimals_0",
    "decimals_1",
    "amount_0",
    "amount_1",
    "amount_0_in",
    "amount_0_out",
    "amount_1_in",
    "amount_1_out",
    "reserve_0",
    "reserve_1",
    "marginal_price",
    "invariant",
    "to_type",
    "tx_type",
]

df = pd.DataFrame(data=transaction_data, columns=col_names)

# Sort dataframe by blockNumber
df = df.sort_values(by=["block_number", "index", "event_index"])
pprint(df)

###################################################################################################
# Write to file
###################################################################################################
# Transform to dataframe
column_types = {
    "timestamp": "Int64",
    "block_number": "Int64",
    "index": "Int64",
    "event_index": "Int64",
    "tx_hash": "str",
    "from_address": "str",
    "to_address": "str",
    "value": "float64",
    "gas": "float64",
    "gas_price": "float64",
    "max_priority_fee_per_gas": "float64",
    "max_fee_per_gas": "float64",
    "event_type": "str",
    "dex_symbol": "str",
    "symbol_0": "str",
    "symbol_1": "str",
    "decimals_0": "Int64",
    "decimals_1": "Int64",
    "amount_0": "float64",
    "amount_1": "float64",
    "amount_0_in": "float64",
    "amount_0_out": "float64",
    "amount_1_in": "float64",
    "amount_1_out": "float64",
    "reserve_0": "float64",
    "reserve_1": "float64",
    "marginal_price": "float64",
    "invariant": "float64",
    "to_type": "str",
    "tx_type": "Int64",
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

logger.error(
    "Elapsed time: %d days, %02d:%02d:%02d", days, hours, minutes, seconds
)

pprint(
    f"Elapsed time: {days} days, {hours:02}:{minutes:02}:{seconds:02}"
)
