# Import packages
import time
start = time.time()
import sys
import os
import multiprocessing
import logging
import pandas as pd
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../'))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v3 import parse_uni_v3_events

# Set up logger
path_logs = constants.path_logs
log_name = 'scripts/data_processing/uniswap_v3/eth_usdc.log'
logging.basicConfig(filename=path_logs + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data
#path_uni_v3_by_positions = constants.path_uni_v3_by_positions
#file_out = os.path.join(constants.path_uni_v3_test_data_dir, 'parsed_trades_only_usdc_weth.csv')
#file_out_selected = os.path.join(constants.path_uni_v3_test_data_dir, 'parsed_trades_only_usdc_weth_selected.csv')

# Full data set
path_uni_v3_by_positions = '/media/m2_front/research/data/trueblocks_lists/uniswap_v3/2023-11-23_eth_usdc_05_positions_october_test.json'
file_out = '/media/m2_front/research/data/trueblocks_lists/uniswap_v3/test_parse/node_test.csv'
file_out_selected ='/media/m2_front/research/data/trueblocks_lists/uniswap_v3/test_parse/node_test_selected.csv'

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
data = general_helpers.load_json(path_uni_v3_by_positions)

# Flatten the dict into a list of tuples
block_index_pairs = [(block, index) for block, indexes in data.items() for index in indexes]

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
        tx_data, receipt_data, block_data = general_helpers.get_tx_receipt_block_by_index(hex(int(block_number)),
                                                                                hex(int(index)))
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect meta data
    try:
        timestamp = block_data['timestamp']
        timestamp = int(timestamp, 0) # from hex to int

        hash = tx_data['hash']
        from_address = tx_data['from']
        to_address = tx_data['to']
        tx_type = int(tx_data['type'], 16)

        value = int(tx_data['value'], 16)
        gas = int(tx_data['gas'], 16)
        gasPrice = int(tx_data['gasPrice'], 16)
        total_gas_cost = gas * gasPrice

        if int(tx_data['type'], 16) == 2: # EIP-1559 (type 2) transactions
            maxPriorityFeePerGas = int(tx_data['maxPriorityFeePerGas'], 16)
            maxFeePerGas = int(tx_data['maxFeePerGas'], 16)
        else: # Legacy (type 0) and EIP-2930 (type 1) transactions
            maxPriorityFeePerGas = 0
            maxFeePerGas = 0

    except Exception as e:
        logger.error(e, exc_info=True)

    # Parse trades
    try:
        logs = receipt_data['logs']
        topics_0 = general_helpers.get_topics_0(logs)
        swap_indexes = general_helpers.get_event_index(topics_0, constants.uniswap_v3_swap_event)

        # Load ABI
        path_uniswap_v3_pair_abi = constants.path_uniswap_v3_pair_abi
        uniswap_v3_pair_abi = general_helpers.load_abi(constants.path_uniswap_v3_pair_abi)
        path_erc20_abi = constants.path_erc20_abi
        erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)

        trades = parse_uni_v3_events.parse_v3_trades(logs, swap_indexes, erc20_abi, uniswap_v3_pair_abi)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Append txes to global list
    try:
        for trade in trades:
            dex_symbol = trade[0]
            symbol_0 = trade[1]
            symbol_1 = trade[2]
            decimals_0 = trade[3]
            decimals_1 = trade[4]
            amount0 = trade[5]
            amount1 = trade[6]
            liquidity = trade[7]
            tick = trade[8]
            sqrtPriceX96 = trade[9]
            price = trade[10]
            e_price = -amount0/amount1
            data = [timestamp, block_number, index, hash, from_address, to_address, value,
                    total_gas_cost, gas, gasPrice,
                         maxPriorityFeePerGas, maxFeePerGas, dex_symbol, symbol_0,
                        symbol_1, decimals_0, decimals_1, amount0, amount1, liquidity, tick,
                    sqrtPriceX96, price, e_price]
            if symbol_0 == "USDC" and symbol_1 == "WETH":
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
    pool.starmap(parse_transaction, block_index_pairs)

    pool.close()
    pool.join() # Synchronization point needed for this to work
    transaction_data = list(L)

#pprint(transaction_data)

###################################################################################################
# Write to file
###################################################################################################
# Transform to dataframe
col_names = ['timestamp', 'block_number', 'index', 'hash', 'from_address', 'to_address', 'value',
             'total_gas_cost',
             'gas', 'gasPrice', 'maxPriorityFeePerGas', 'maxFeePerGas', 'dex_symbol', 'symbol_0',
             'symbol_1', 'decimals_0', 'decimals_1', 'amount0', 'amount1', 'liquidity', 'tick',
             'sqrtPriceX96', 'price', 'e_price']

df = pd.DataFrame(data=transaction_data, columns=col_names)

# Sort dataframe by blockNumber
df = df.sort_values(by=['block_number', 'index'])

# Select only specific columns
# Selecting specific columns
selected_columns = ['timestamp', 'hash', 'symbol_0', 'symbol_1', 'amount0', 'amount1', 'e_price', 'total_gas_cost']
df_selected = df[selected_columns]

pprint(df)
pprint(df_selected)

# Save dataframe as csv
df.to_csv(file_out, sep=',', index=False)
df_selected.to_csv(file_out_selected, sep=',', index=False)

###################################################################################################
# Print elapsed time with days included
###################################################################################################
end = time.time()
elapsed_seconds = int(end - start)
days, rem = divmod(elapsed_seconds, 86400)
hours, rem = divmod(rem, 3600)
minutes, seconds = divmod(rem, 60)
pprint("Elapsed time: {} days, {:0>2}:{:0>2}:{:0>2}".format(days, hours, minutes, seconds))
