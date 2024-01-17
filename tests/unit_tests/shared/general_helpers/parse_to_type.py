# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../../'))

# Import scripts
from shared import general_helpers
from shared import constants

# Set up logger
path_logs = constants.path_logs
log_name = 'tests/default_test.log'
logging.basicConfig(filename=path_logs + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

# Import mev contracts list
mev_contracts = general_helpers.load_txt(constants.path_mev_contracts) # Generator object
mev_contracts_list = list(mev_contracts)

# Construct to_addresses
to_addresses = [constants.uniswap_v3_router_address, constants.uniswap_v3_positions_nft_address,
                constants.uniswap_v3_migrator_address, constants.uniswap_universal_router_address,
                '0xEB4c5AB9B36437f969888be99AF42fC9087005A5', '0xother']


for to_address in to_addresses:
    to_type = general_helpers.parse_to_type(to_address, mev_contracts_list)
    pprint(to_type)
