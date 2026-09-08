"""
This file contains constants used by the dexamine Python package.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import os

########################################################################################
# Ethereum node
########################################################################################
# Convenience default for a locally running node. Every public API entrypoint takes
# `node_url` explicitly; this is only a suggested value, not a fallback. An archive node
# is not required: pool and token metadata are read at the latest block. What is required
# is an endpoint that still serves the blocks and receipts being parsed.
NODE_URL = "http://localhost:8545"

########################################################################################
# General paths
########################################################################################
# Absolute path of the directory where constants.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

########################################################################################
# General Paths (ABIs, lists, data)
########################################################################################
# Path to general ABIs
PATH_ERC20_ABI = os.path.join(BASE_DIR, "../resources/abis/erc20/ERC20_abi.json")
PATH_ERC20_BYTES_ABI = os.path.join(
    BASE_DIR, "../resources/abis/erc20/ERC20_bytes32_abi.json"
)

########################################################################################
# General Smart Contract Addresses
########################################################################################
USDC_TOKEN_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

########################################################################################
# Uniswap v2
########################################################################################
# Uniswap v2 smart contract addresses
UNISWAP_V2_ROUTER_ADDRESS = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
UNISWAP_V2_ROUTER_2_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Path to Uniswap v2 ABIs
PATH_UNISWAP_V2_PAIR_ABI = os.path.join(
    BASE_DIR, "../resources/abis/uniswap_v2/IUniswapV2Pair.json"
)

# Uniswap v2 events
UNISWAP_V2_SWAP_EVENT = (
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
)
UNISWAP_V2_SYNC_EVENT = (
    "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
)
UNISWAP_V2_MINT_EVENT = (
    "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"
)
UNISWAP_V2_BURN_EVENT = (
    "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496"
)

# Uniswap v2 pools
UNISWAP_V2_USDC_WETH_ADDRESS = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"

########################################################################################
# Uniswap v3
########################################################################################
# Uniswap v3 smart contract addresses
# https://docs.uniswap.org/contracts/v3/reference/deployments
UNISWAP_V3_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
UNISWAP_V3_ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
UNISWAP_V3_ROUTER_2_ADDRESS = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
UNISWAP_V3_POSITIONS_NFT_ADDRESS = "0xC36442b4a4522E871399CD717aBDD847Ab11FE88"
UNISWAP_V3_MIGRATOR_ADDRESS = "0xA5644E29708357803b5A882D272c41cC0dF92B34"

# Universal router (also routes to v2)
UNISWAP_UNIVERSAL_ROUTER_ADDRESS = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD"

# Universal router v4 (also routes to v2/v3)
UNISWAP_UNIVERSAL_ROUTER_V4_ADDRESS = "0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af"

# Path to Uniswap v3 ABIs
PATH_UNISWAP_V3_PAIR_ABI = os.path.join(
    BASE_DIR, "../resources/abis/uniswap_v3/UniswapV3PoolABI.json"
)

# Uniswap v3 events
UNISWAP_V3_SWAP_EVENT = (
    "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
)
UNISWAP_V3_MINT_EVENT = (
    "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"
)
UNISWAP_V3_BURN_EVENT = (
    "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"
)

UNISWAP_V3_INCREASE_LIQUIDITY_EVENT = (
    "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f"
)
UNISWAP_V3_DECREASE_LIQUIDITY_EVENT = (
    "0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4"
)

# Uniswap v3 pools
UNISWAP_V3_USDC_WETH_5BPS_ADDRESS = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"

########################################################################################
# Lists
########################################################################################
# Canonical Uniswap router and periphery deployments on Ethereum mainnet.
#
# This is a set of *protocol constants*, not a curated behavioural list: each entry is
# an official Uniswap deployment documented at
# https://docs.uniswap.org/contracts/v2/reference/smart-contracts/ and
# https://docs.uniswap.org/contracts/v3/reference/deployments. It is used by
# `dexamine.shared.general_helpers.parse_to_type` to distinguish transactions sent
# directly to Uniswap ("uniswap_router") from transactions routed through any other
# contract ("other_contract").
#
# To extend: append a new module-level constant above and add it here when Uniswap
# deploys an additional router. Nothing else in the package needs to change.
uniswap_address_list = [
    UNISWAP_V3_ROUTER_ADDRESS,
    UNISWAP_V3_POSITIONS_NFT_ADDRESS,
    UNISWAP_UNIVERSAL_ROUTER_ADDRESS,
    UNISWAP_UNIVERSAL_ROUTER_V4_ADDRESS,
    UNISWAP_V3_MIGRATOR_ADDRESS,
    UNISWAP_V2_ROUTER_ADDRESS,
    UNISWAP_V3_ROUTER_2_ADDRESS,
    UNISWAP_V2_ROUTER_2_ADDRESS,
]
