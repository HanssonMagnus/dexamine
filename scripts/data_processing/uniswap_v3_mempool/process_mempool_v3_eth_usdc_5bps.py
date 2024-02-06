# Output run 2024-01-09:
# [5694177 rows x 26 columns]
# 'Elapsed time: 0 days, 06:14:56'
#
# Import packages
import time
start = time.time()
import sys
import os
import multiprocessing
import logging
import pandas as pd
from pprint import pprint
from eth_utils import encode_hex, to_bytes

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../'))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v3 import parse_uni_v3_events

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = 'scripts/data_processing/uniswap_v3_mempool/eth_usdc.log'
logging.basicConfig(filename=PATH_LOGS + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data

# Full data set
directory_path = '/media/m2_front/research/data/projects/quantum_defi/0_raw/mempool/october/'
file_out = '/media/m2_front/research/data/projects/quantum_defi/1_raw/mempool/october/usdc_eth_5bps_october.csv'

###################################################################################################
# Load parquet data, extract the rawTx column, and add to list
###################################################################################################
def load_and_extract_columns_as_tuples(directory_path, columns):
    if len(columns) != 2:
        raise ValueError("Only two columns should be specified")

    tuples_list = []  # List to hold tuples of (raw_tx, hash)

    # List all Parquet files in the directory
    parquet_files = [f for f in os.listdir(directory_path) if f.endswith('.parquet')]

    for file in parquet_files:
        file_path = os.path.join(directory_path, file)

        # Read the Parquet file
        df = pd.read_parquet(file_path)

        # Check if both columns exist
        if all(col in df.columns for col in columns):
            # Extract tuples of (raw_tx, hash) and append to the list
            tuples = list(zip(df[columns[0]], df[columns[1]]))
            tuples_list.extend(tuples)
        else:
            missing_cols = [col for col in columns if col not in df.columns]
            print(f"Missing column(s) {missing_cols} in file: {file}")

    return tuples_list

# Usage
columns = ['hash', 'rawTx']
data_tuples = load_and_extract_columns_as_tuples(directory_path, columns)

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)

###################################################################################################
# Prepare arguments for multiprocessing
###################################################################################################
args_for_multiprocessing = [(hash, raw_tx, erc20_abi) for hash, raw_tx in data_tuples]

###################################################################################################
# Def multiprocess function
#
# Values from the tx:
# dict_keys(['blockHash', 'blockNumber', 'from', 'gas', 'gasPrice', 'maxPriorityFeePerGas',
# 'maxFeePerGas', 'hash', 'input', 'nonce', 'to', 'transactionIndex', 'value', 'type',
# 'accessList', 'chainId', 'v', 'r', 's'])
###################################################################################################
def parse_raw_transaction(hash, raw_tx, erc20_abi):
    swaps = None # Initialize swaps to None

    try:
        raw_tx = encode_hex(raw_tx)
        decoded_tx = general_helpers.decode_mempool_tx(raw_tx)
        data = decoded_tx['_data']
    except Exception as e:
        logger.error(e, exc_info=True)

    try:
        swaps = parse_uni_v3_raw_tx.parse_v3_exact_input_single(data, erc20_abi, constants.USDC_TOKEN_ADDRESS,
                                                            constants.WETH_TOKEN_ADDRESS)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Return function if there are no Uniswap v3 swaps
    if swaps is None:
        return





    # Collect meta data
    try:
        to_address = decoded_tx['_to']

        # to_address is None if it's a contract creating transactions
        if to_address is None:
            to_address = 'contract_creation'

        timestamp = block_data['timestamp']
        timestamp = int(timestamp, 0) # from hex to int

        from_address = tx_data['from']
        tx_type = int(tx_data['type'], 16)

        value = int(tx_data['value'], 16)
        gas = int(tx_data['gas'], 16)
        gasPrice = int(tx_data['gasPrice'], 16)

        if int(tx_data['type'], 16) == 2: # EIP-1559 (type 2) transactions
            maxPriorityFeePerGas = int(tx_data['maxPriorityFeePerGas'], 16)
            maxFeePerGas = int(tx_data['maxFeePerGas'], 16)
        else: # Legacy (type 0) and EIP-2930 (type 1) transactions
            maxPriorityFeePerGas = 0
            maxFeePerGas = 0

    except Exception as e:
        logger.error(e, exc_info=True)

    # Identify type of transaction (MEV, DeFi, UNI)
    try:
        to_type = general_helpers.parse_to_type(to_address, mev_contracts_list)
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
            amount_0 = event[6]
            amount_1 = event[7]
            liquidity = event[8]
            tick = event[9]
            sqrt_price_x96 = event[10]
            price = event[11]
            tick_lower = event[12]
            tick_upper = event[13]
            data = [timestamp, block_number, index, hash, from_address, to_address, value, gas,
                    gasPrice, maxPriorityFeePerGas, maxFeePerGas, type_of_event, dex_symbol,
                    symbol_0, symbol_1, decimals_0, decimals_1, amount_0, amount_1, liquidity,
                    tick, sqrt_price_x96, price, tick_lower, tick_upper, to_type]
            L.append(data)
    except Exception as e:
        logger.error(e, exc_info=True)

###################################################################################################
# Collect transactions with the multiprocessing library
###################################################################################################
with multiprocessing.Manager() as manager:
    L = manager.list() # Can be shared between multiprocesses
    n_cpu = multiprocessing.cpu_count() # n threads
    # Processes outside of the loop otherwise too many files error
    # I've previously had trouble with too high maxtasksperchild and set it to 2, however, ChatGPT
    # thinks I can increase it a bit. So I should try it out for increased performance. Increasing
    # it from 2 to 15, made the test code run at 0.8s instead of 2.04. However, increating to 40
    # did not improve the speed further.
    pool = multiprocessing.Pool(n_cpu, maxtasksperchild=100)

    # Map get_tx to a range of blocks
    #pool.imap_unordered(parse_transaction, hashes_list)
    pool.starmap(parse_transaction, args_for_multiprocessing)

    pool.close()
    pool.join() # Synchronization point needed for this to work
    transaction_data = list(L)

#pprint(transaction_data)

###################################################################################################
# Write to file
###################################################################################################
# Transform to dataframe
#col_names = ['block', 'tx_index', 'hash', 'from', 'to', 'value', 'gas', 'gas_price', 'gas_tip_cap',
#             'gas_fee_cap']
col_names= ['timestamp', 'block_number', 'index', 'hash', 'from_address', 'to_address', 'value',
            'gas', 'gasPrice', 'maxPriorityFeePerGas', 'maxFeePerGas', 'type_of_event', 'dex_symbol',
            'symbol_0', 'symbol_1', 'decimals_0', 'decimals_1', 'amount_0', 'amount_1', 'liquidity',
            'tick', 'sqrt_price_x96', 'price', 'tick_lower', 'tick_upper', 'to_type']

df = pd.DataFrame(data=transaction_data, columns=col_names)

# Sort dataframe by blockNumber
df = df.sort_values(by=['block_number', 'index'])
pprint(df)

# Set the display option to show the full content of the column
#pd.set_option('display.max_colwidth', None)
#pprint(df[df['to_type']=='defi']['hash'])

# Save dataframe as csv
df.to_csv(file_out, sep=',', index=False)

###################################################################################################
# Print elapsed time with days included
###################################################################################################
end = time.time()
elapsed_seconds = int(end - start)
days, rem = divmod(elapsed_seconds, 86400)
hours, rem = divmod(rem, 3600)
minutes, seconds = divmod(rem, 60)
pprint("Elapsed time: {} days, {:0>2}:{:0>2}:{:0>2}".format(days, hours, minutes, seconds))
