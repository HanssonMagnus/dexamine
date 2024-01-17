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
path_logs = constants.path_logs
log_name = 'scripts/data_processing/uniswap_v3_mempool/eth_usdc.log'
logging.basicConfig(filename=path_logs + log_name, level=logging.ERROR,
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

# Step 1: Load Parquet Files
def load_parquet_files(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.parquet')]
    df_list = [pd.read_parquet(file) for file in files]
    return pd.concat(df_list, ignore_index=True)

# Step 2: Define Parsing Function
def parse_raw_tx_data(raw_tx):
    # Extract and parse the 'data' field from raw_tx
    # Return the parsed information or None if parsing fails
    raw_tx = encode_hex(raw_tx)
    decoded_tx = general_helpers.decode_mempool_tx(raw_tx)
    data = decoded_tx['_data']

    try:
        swaps = parse_uni_v3_raw_tx.parse_v3_exact_input_single(data, erc20_abi, constants.usdc_token,
                                                            constants.weth_token)
    except Exception as e:
        print(e)
    pass

# Step 3: Apply Filtering and Parsing
def filter_and_parse_transactions(df):
    df['parsed_data'] = df['raw_tx'].apply(parse_raw_tx_data)
    # Apply your specific filtering criteria
    # For example, filter based on a condition in 'parsed_data'
    filtered_df = df[df['parsed_data'].apply(your_filtering_criteria)]
    return filtered_df

# Step 4: Save as CSV
def save_to_csv(df, output_file):
    df.to_csv(output_file, index=False)

# Usage
directory_path = '/path/to/your/parquet/files'
all_transactions_df = load_parquet_files(directory_path)
filtered_transactions_df = filter_and_parse_transactions(all_transactions_df)
output_csv_file = '/path/to/save/filtered_data.csv'
save_to_csv(filtered_transactions_df, output_csv_file)
