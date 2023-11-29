# Import packages
import os

# Set path for logging
path_logs = '/media/m2_front/research/logs/node-data/'

# Absolute path of the directory where constants.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the test data directory
path_uni_v2_by_positions = os.path.join(BASE_DIR, '../test_data/uniswap_v2/uni_v2_by_positions.json')

###################################################################################################
# Uniswap v2
###################################################################################################
# Path to Uniswap v2 ABIs
path_uniswap_v2_erc20_abi = os.path.join(BASE_DIR, '../abis/uniswap_v2/IUniswapV2ERC20.json')
path_uniswap_v2_pair_abi = os.path.join(BASE_DIR, '../abis/uniswap_v2/IUniswapV2Pair.json')

# Unsiwp v2 events
uniswap_v2_swap_event = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
uniswap_v2_sync_event = '0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1'

###################################################################################################
# Uniswap v3
###################################################################################################
