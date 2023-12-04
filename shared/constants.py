# Import packages
import os

###################################################################################################
# General paths
###################################################################################################
# Set path for logging
path_logs = '/media/m2_front/research/logs/node-data/'

# Absolute path of the directory where constants.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

###################################################################################################
# Uniswap v2
###################################################################################################
# Path to Uniswap v2 ABIs
path_uniswap_v2_erc20_abi = os.path.join(BASE_DIR, '../abis/uniswap_v2/IUniswapV2ERC20.json')
path_uniswap_v2_pair_abi = os.path.join(BASE_DIR, '../abis/uniswap_v2/IUniswapV2Pair.json')

# Path to Uniswap v2 test data
path_uni_v2_test_data_dir = os.path.join(BASE_DIR, '../test_data/uniswap_v2/')
path_uni_v2_by_positions = os.path.join(BASE_DIR, '../test_data/uniswap_v2/uni_v2_by_positions.json')

# Unsiwp v2 events
uniswap_v2_swap_event = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
uniswap_v2_sync_event = '0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1'
uniswap_v2_mint_event = '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f'
uniswap_v2_burn_event = '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496'

# Uniswap v2 pools
uniswap_v2_usdc_eth = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'

###################################################################################################
# Uniswap v3
###################################################################################################
# Path to Uniswap v3 test data
path_uni_v3_by_positions = os.path.join(BASE_DIR, '../test_data/uniswap_v3/uni_v3_by_positions.json')
