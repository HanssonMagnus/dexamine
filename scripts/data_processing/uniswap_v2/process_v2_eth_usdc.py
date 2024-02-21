# Output run 2024-02-16:
# [5088482 rows x 28 columns]
# 'Elapsed time: 0 days, 05:46:43'
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

# Import modules
from dexamine.shared import constants, general_helpers
from dexamine.parsers import uniswap_v2_parser

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = 'scripts/data_processing/uniswap_v2/usdc_weth.log'
logging.basicConfig(filename=PATH_LOGS + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data
#PATH_UNISWAP_V2_BY_POSITIONS = constants.PATH_UNISWAP_V2_BY_POSITIONS
#file_out = os.path.join(constants.PATH_UNISWAP_V2_TEST_DATA_DIR, 'parsed_events_usdc_weth.csv')

# Full data set
PATH_UNISWAP_V2_BY_POSITIONS = "/media/m2_front/research/data/trueblocks_lists/uniswap_v2/usdc_weth/2024-02-13_usdc_weth_positions.json"
file_out = "/media/m2_front/research/data/projects/dex_price_discovery/uniswap_v2/1_parsed/events_usdc_weth.csv"

# Check that the output path exists
if not os.path.exists(os.path.dirname(file_out)):
    logger.error("file_out directory does not exist.")
    sys.exit(1)

###################################################################################################
# Load tx data as a json dict.
###################################################################################################
data = general_helpers.load_json(PATH_UNISWAP_V2_BY_POSITIONS)

# Flatten the dict into a list of tuples
block_index_pairs = [(block, index) for block, indexes in data.items() for index in indexes]

# Smart contract address of USDC-WETH pool
UNISWAP_V2_USDC_WETH_ADDRESS = constants.UNISWAP_V2_USDC_WETH_ADDRESS

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
erc20_bytes32_abi = general_helpers.load_abi(constants.PATH_ERC20_BYTES_ABI)
uniswap_v2_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V2_PAIR_ABI)

###################################################################################################
# Load MEV contracts
###################################################################################################
mev_contracts = general_helpers.load_txt(constants.PATH_MEV_CONTRACTS) # Generator object
mev_contracts_list = list(mev_contracts)

###################################################################################################
# Prepare arguments for multiprocessing
###################################################################################################
args_for_multiprocessing = [(block, index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi, mev_contracts_list) for block, index in block_index_pairs]

###################################################################################################
# Def multiprocess function
#
# Values from the tx:
# dict_keys(['blockHash', 'blockNumber', 'from', 'gas', 'gasPrice', 'maxPriorityFeePerGas',
# 'maxFeePerGas', 'hash', 'input', 'nonce', 'to', 'transactionIndex', 'value', 'type',
# 'accessList', 'chainId', 'v', 'r', 's'])
###################################################################################################
def parse_transaction(block_number, index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi, mev_contracts_list):
    events = None # Initialize events to None

    try:
        tx_data, receipt_data, block_data = general_helpers.get_tx_receipt_block_by_index(hex(int(block_number)),
                                                                                hex(int(index)))
    except Exception as e:
        logger.error(e, exc_info=True)

    # Collect events
    try:
        logs = receipt_data['logs']
        events = uniswap_v2_parser.parse_all_uniswap_v2_events(logs,
                                                         erc20_abi=erc20_abi,
                                                         erc20_bytes32_abi=erc20_bytes32_abi,
                                                         uniswap_v2_pair_abi=uniswap_v2_pair_abi,
                                                         exchange_pair_address=UNISWAP_V2_USDC_WETH_ADDRESS)
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
            amount_0 = event['amount_0']
            amount_0_in = event['amount_0_in']
            amount_0_out = event['amount_0_out']
            amount_1 = event['amount_1']
            amount_1_in = event['amount_1_in']
            amount_1_out = event['amount_1_out']
            decimals_0 = event['decimals_0']
            decimals_1 = event['decimals_1']
            dex_symbol = event['dex_symbol']
            event_type = event['event_type']
            invariant = event['invariant']
            mid_price = event['mid_price']
            reserve_0 = event['reserve_0']
            reserve_1 = event['reserve_1']
            symbol_0 = event['symbol_0']
            symbol_1 = event['symbol_1']

            data = [timestamp, block_number, index, hash, from_address, to_address, value, gas, gasPrice,
                         maxPriorityFeePerGas, maxFeePerGas, event_type, dex_symbol, symbol_0,
                        symbol_1, decimals_0, decimals_1, amount_0, amount_1,
                    amount_0_in, amount_0_out, amount_1_in, amount_1_out, reserve_0,
                    reserve_1, mid_price, invariant, to_type]
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
            'symbol_0', 'symbol_1', 'decimals_0', 'decimals_1', 'amount_0', 'amount_1',
            'amount_0_in', 'amount_0_out', 'amount_1_in', 'amount_1_out', 'reserve_0',
            'reserve_1', 'mid_price', 'invariant', 'to_type']

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
