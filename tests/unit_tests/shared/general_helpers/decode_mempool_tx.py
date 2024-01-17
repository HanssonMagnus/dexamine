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

# Path to your Parquet file
file_path = constants.path_mempool_test_data

# Read the Parquet file
try:
    df = pd.read_parquet(file_path, engine='pyarrow')
except Exception as e:
    print(f"Error reading the Parquet file: {e}")

# Select sub-sample
df = df[0:10]
#pprint(df.columns)

for rawTx in df['rawTx']:
    rawTx = encode_hex(rawTx)

    #signed_tx_as_bytes = to_bytes(hexstr=rawTx)
    #decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
    #decoded_tx = decoded_tx.__dict__

    pprint(rawTx)
    decoded_tx = general_helpers.decode_mempool_tx(rawTx)
    pprint(decoded_tx)



