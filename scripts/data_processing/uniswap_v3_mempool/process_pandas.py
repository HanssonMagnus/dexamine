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
from parsers.uniswap_v3 import parse_uni_v3_raw_tx

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

# Test data
#directory_path='/home/magnus/Git/HanssonMagnus/research/node-data/test_data/mempool'
#directory_path = '/media/m2_front/research/data/projects/quantum_defi/0_raw/mempool/october_test/'
#output_csv_file='/home/magnus/Git/HanssonMagnus/research/node-data/test_data/mempool/2023-10-01_test_parsed.csv'

# Full data set
directory_path = '/media/m2_front/research/data/projects/quantum_defi/0_raw/mempool/october/'
output_csv_file = '/media/m2_front/research/data/projects/quantum_defi/1_parsed/mempool/october/usdc_eth_5bps_october.csv'

###################################################################################################
# Load ABIs
###################################################################################################
erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)

###################################################################################################
# Step 1: Load Parquet Files
###################################################################################################
def load_parquet_files(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.parquet')]
    df_list = [pd.read_parquet(file) for file in files]
    return pd.concat(df_list, ignore_index=True)

###################################################################################################
# Step 2: Define Parsing Function
###################################################################################################
def parse_raw_tx_data(raw_tx, transaction_info, erc20_abi):
    # Extract and parse the 'data' field from raw_tx
    # Return the parsed information or None if parsing fails
    raw_tx = encode_hex(raw_tx)
    decoded_tx = general_helpers.decode_mempool_tx(raw_tx)
    data = decoded_tx['_data']

    parsed_swaps = []
    try:
        swaps = parse_uni_v3_raw_tx.parse_v3_exact_input_single(data, erc20_abi,
                                                                constants.USDC_TOKEN_ADDRESS,
                                                                constants.WETH_TOKEN_ADDRESS)
        if not swaps:
            return parsed_swaps
        for swap in swaps:
            swap_info = {'timestamp': transaction_info['timestamp'],
                         'hash': transaction_info['hash'],
                         'chainId': transaction_info['chainId'],
                         'from': transaction_info['from'],
                         'to': transaction_info['to'],
                         'value': transaction_info['value'],
                         'nonce': transaction_info['nonce'],
                         'gas': transaction_info['gas'],
                         'gasPrice': transaction_info['gasPrice'],
                         'gasTipCap': transaction_info['gasTipCap'],
                         'gasFeeCap': transaction_info['gasFeeCap'],
                         'dataSize': transaction_info['dataSize'],
                         'data4Bytes': transaction_info['data4Bytes'],
                         'sources': transaction_info['sources'],
                         'includedAtBlockHeight': transaction_info['includedAtBlockHeight'],
                         'includedBlockTimestamp': transaction_info['includedBlockTimestamp'],
                         'inclusionDelayMs': transaction_info['inclusionDelayMs']
                         #'rawTx': transaction_info['rawTx'],
                         }  # Include necessary transaction fields

            swap_info.update({ 'swap_type': swap[0],
                                 'symbol_in': swap[1],
                                 'symbol_out': swap[2],
                                 'decimals_in': swap[3],
                                 'decimals_out': swap[4],
                                 'token_in_address': swap[5],
                                 'token_out_address': swap[6],
                                 'pair_fee': swap[7],
                                 'recipient': swap[8],
                                 'deadline': swap[9],
                                 'amount_in': swap[10],
                                 'amount_out_minimum': swap[11],
                                 'limit_exchange_rate': swap[12],
                                 'sqrt_price_limit_x96': swap[13]})  # Add all swap attributes here
            parsed_swaps.append(swap_info)

    except Exception as e:
        logger.error(f"Error parsing raw_tx: {e}")

    return parsed_swaps

###################################################################################################
# Step 3: Apply Parsing
###################################################################################################
def parse_transactions(df, erc20_abi):
    parsed_swaps_list = []
    for index, row in df.iterrows():
        transaction_info = row.to_dict()  # Get transaction info as a dictionary
        parsed_swaps = parse_raw_tx_data(row['rawTx'], transaction_info, erc20_abi)
        if parsed_swaps:
            parsed_swaps_list.extend(parsed_swaps)

    parsed_swaps_df = pd.DataFrame(parsed_swaps_list)

    return parsed_swaps_df

###################################################################################################
# Step 4: Save as CSV
###################################################################################################
def save_to_csv(df, output_file):
    df.to_csv(output_file, index=False, chunksize=100)

###################################################################################################
# Step 5: Usage
###################################################################################################
all_transactions_df = load_parquet_files(directory_path)
#pprint(all_transactions_df)

parsed_transactions_df = parse_transactions(all_transactions_df, erc20_abi)
save_to_csv(parsed_transactions_df, output_csv_file)
