# Import packages
import sys
import os
import logging
from pprint import pprint
import pandas as pd

from eth_utils import encode_hex, to_bytes
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v3 import parse_uni_v3_raw_tx

# Path to your Parquet file
#file_path = constants.path_mempool_test_data
file_path = '/media/m2_front/research/data/projects/quantum_defi/0_raw/mempool/october/2023-10-01.parquet'

# Read the Parquet file
try:
    df = pd.read_parquet(file_path, engine='pyarrow')
except Exception as e:
    print(f"Error reading the Parquet file: {e}")

# Load ABI
erc20_abi = general_helpers.load_abi(constants.path_erc20_abi)

# Select sub-sample
#df = df[0:1]
pprint(df.columns)


sig_1 = '0x414bf389'
sig_2 = '0x41060ae0'

#df_sig = df[df['data4Bytes'] == sig_1]
#pprint(df_sig['data4Bytes'])

counter = 0
for rawTx in df['rawTx']:
    rawTx = encode_hex(rawTx)

    decoded_tx = general_helpers.decode_mempool_tx(rawTx)

    #pprint(decoded_tx)

    data = decoded_tx['_data']

    try:
        swaps = parse_uni_v3_raw_tx.parse_v3_exact_input_single(data, erc20_abi, constants.usdc_token,
                                                            constants.weth_token)
        #swaps = parse_uni_v3_raw_tx.parse_v3_exact_input_single(data, erc20_abi)
    except Exception as e:
        print(e)

    if swaps:
        counter +=1
        pprint(swaps)
pprint(counter)




