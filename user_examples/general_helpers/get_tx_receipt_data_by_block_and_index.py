# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from ethereum_defi_parser.shared import general_helpers, constants

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = 'tests/default_test.log'
logging.basicConfig(filename=PATH_LOGS + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

# Import test data
data = general_helpers.get_json_test_data("uniswap_v3/uniswap_v3_by_positions.json")

blocks = list(data.keys())

# Parse transations
#blocks = blocks[83:84] # test with only 1 tx (2 swaps)
blocks = blocks[0:1] # test with only 1 tx (2 swaps)
for block in blocks:
    tx_indexes = data[block]
    for index in tx_indexes:
        # Get transaction data
        try:
            tx, receipt, block_data = general_helpers.get_tx_receipt_block_by_index(hex(int(block)),
                                                                                hex(int(index)))
        except Exception as e:
            logger.error(e, exc_info=True)

        #pprint(tx)
        #for j in range(len(receipt['logs'])):
        #    pprint(receipt['logs'][j]['transactionHash'])
        #pprint(block_data)
        pprint(receipt)
