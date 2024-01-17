# Output run 2023-12-11:
# [4156261 rows x 24 columns]
# 'Elapsed time: 0 days, 04:40:35'
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

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../'))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v2 import parse_uni_v2_events

# Set up logger
path_logs = constants.path_logs
log_name = 'scripts/data_processing/uniswap_v2/eth_usdc.log'
logging.basicConfig(filename=path_logs + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data
#path_uni_v2_by_positions = constants.path_uni_v2_by_positions
#file_out = os.path.join(constants.path_uni_v2_test_data_dir, 'parsed_events_usdc_weth.csv')

# Full data set
path_uni_v2_by_positions = '/media/m2_front/research/data/projects/dex_price_discovery/0_raw/txes_eth_usdc.json'
file_out = '/media/m2_front/research/data/projects/dex_price_discovery/6_new_parser/events_usdc_weth.csv'

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
data = general_helpers.load_json(path_uni_v2_by_positions)

# Flatten the dict into a list of tuples
block_index_pairs = [(block, index) for block, indexes in data.items() for index in indexes]

# Smart contract address of USDC-WETH pool
uniswap_v2_usdc_eth = constants.uniswap_v2_usdc_eth

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)
uniswap_v2_pair_abi = general_helpers.load_abi(constants.path_uniswap_v2_pair_abi)

###################################################################################################
# Load MEV contracts
###################################################################################################
mev_contracts = general_helpers.load_txt(constants.path_mev_contracts) # Generator object
mev_contracts_list = list(mev_contracts)

###################################################################################################
# Prepare arguments for multiprocessing
###################################################################################################
args_for_multiprocessing = [(block, index, erc20_abi, uniswap_v2_pair_abi, mev_contracts_list) for block, index in block_index_pairs]

###################################################################################################
# Def multiprocess function
#
# Values from the tx:
# dict_keys(['blockHash', 'blockNumber', 'from', 'gas', 'gasPrice', 'maxPriorityFeePerGas',
# 'maxFeePerGas', 'hash', 'input', 'nonce', 'to', 'transactionIndex', 'value', 'type',
# 'accessList', 'chainId', 'v', 'r', 's'])
###################################################################################################
def parse_transaction(block_number, index, erc20_abi, uniswap_v2_pair_abi, mev_contracts_list):
    events = None # Initialize events to None

    try:
        tx_data, receipt_data, block_data = general_helpers.get_tx_receipt_block_by_index(hex(int(block_number)),
                                                                                hex(int(index)))
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect events
    try:
        logs = receipt_data['logs']
        events = parse_uni_v2_events.parse_all_v2_events(logs,
                                                         uniswap_v2_erc20_abi=erc20_abi,
                                                         uniswap_v2_pair_abi=uniswap_v2_pair_abi,
                                                         exchange_pair_address=uniswap_v2_usdc_eth)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Return function if there are no Uniswap v3 events
    if events is None:
        return

    # Collect meta data
    try:
        hash = tx_data['hash']
        to_address = tx_data['to']

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
            dxt = event[6]
            dyt = event[7]
            xt1 = event[8]
            yt1 = event[9]
            pt1 = event[10]
            kt1 = event[11]
            data = [timestamp, block_number, index, hash, from_address, to_address, value, gas, gasPrice,
                         maxPriorityFeePerGas, maxFeePerGas, type_of_event, dex_symbol, symbol_0,
                        symbol_1, decimals_0, decimals_1, dxt, dyt, xt1, yt1, pt1, kt1, to_type]
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
            'symbol_0', 'symbol_1', 'decimals_0', 'decimals_1', 'dxt', 'dyt', 'xt1', 'yt1', 'pt1',
            'kt1', 'to_type']

df = pd.DataFrame(data=transaction_data, columns=col_names)

# Sort dataframe by blockNumber
df = df.sort_values(by=['block_number', 'index'])
pprint(df)

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
