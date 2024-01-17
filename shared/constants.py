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
# General Paths (ABIs, lists, data)
###################################################################################################
# Path to MEV contract list
path_mev_contracts = os.path.join(BASE_DIR, '../lists/mev_contracts_2024-01-09.txt')

# Path to general ABIs
path_erc20_abi = os.path.join(BASE_DIR, '../abis/erc20/ERC20_abi.json')

# Path to Uniswap v2 test data
path_mempool_test_data_dir = os.path.join(BASE_DIR, '../test_data/mempool/')
path_mempool_test_data = os.path.join(BASE_DIR, '../test_data/mempool/2023-10-01_test.parquet')

###################################################################################################
# General Addresses
###################################################################################################
usdc_token = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
weth_token = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

###################################################################################################
# Uniswap v2
###################################################################################################
# Uniswap v2 smart contract addresses
uniswap_v2_router_address = '0xf164fC0Ec4E93095b804a4795bBe1e041497b92a'
uniswap_v2_router_2_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

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
# Uniswap v3 smart contract addresses
# https://docs.uniswap.org/contracts/v3/reference/deployments
uniswap_v3_factory_address = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
uniswap_v3_router_address = '0xE592427A0AEce92De3Edee1F18E0157C05861564'
uniswap_v3_router_2_address = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'
uniswap_v3_positions_nft_address = '0xC36442b4a4522E871399CD717aBDD847Ab11FE88'
uniswap_v3_migrator_address = '0xA5644E29708357803b5A882D272c41cC0dF92B34'

# Universal router (also routes to v2)
uniswap_universal_router_address = '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'

# Path to Uniswap v3 ABIs
path_uniswap_v3_pair_abi = os.path.join(BASE_DIR, '../abis/uniswap_v3/UniswapV3PoolABI.json')

# Path to Uniswap v3 test data
path_uni_v3_test_data_dir = os.path.join(BASE_DIR, '../test_data/uniswap_v3/')
path_uni_v3_by_positions = os.path.join(BASE_DIR, '../test_data/uniswap_v3/uni_v3_by_positions.json')

# Uniswap v3 events
uniswap_v3_swap_event = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
uniswap_v3_mint_event = '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde'
uniswap_v3_burn_event = '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c'

uniswap_v3_increase_liquidity_event = '0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f'
uniswap_v3_decrease_liquidity_event = '0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4'

# Unsiwap v3 pools
uniswap_v3_usdc_eth_5bps = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'
