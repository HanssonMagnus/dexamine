"""
This file contains helper functions for parsers.uniswap_v3.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from web3 import Web3

# Import modules
from dexamine.shared import constants


########################################################################################
# Uniswap v3 general functions
#
# This functions is not used any more!!! Since this logic is moved into the
# UniswapV3Swap class.
########################################################################################
def sqrt_price_x96_to_price(sqrt_price_x96, token0_dec, token1_dec):
    """Convert the sqrt_price_x96 to the regular price and transform it to base units.
    E.g., for the USDC/ETH pair the price will be in dollars per ether, e.g., 2250."""
    price = (10**token1_dec / 10**token0_dec) / (sqrt_price_x96 / 2**96) ** 2
    return price


########################################################################################
# Uniswap v3 ABI call node functions
########################################################################################
def get_v3_pair(*, node_url: str, v3_pair_address: str, uniswap_v3_pair_abi):
    """Get smart contract addresses for the tokens in a v3 pair from node."""
    w3 = Web3(Web3.HTTPProvider(node_url))
    v3_pair_address = Web3.to_checksum_address(v3_pair_address)
    swap_contract = w3.eth.contract(address=v3_pair_address, abi=uniswap_v3_pair_abi)
    token0 = swap_contract.functions.token0().call()
    token1 = swap_contract.functions.token1().call()
    return token0, token1


def get_v3_dex(*, node_url: str, v3_pair_address: str, uniswap_v3_pair_abi):
    """
    Check if the given pool address belongs to Uniswap V3. Uniswap V3 pools are not
    ERC20 contracts, thus there is no way to get the name of the DEX only to validate if
    it is a known DEX.

    Parameters:
    v3_pair_address (str): The address of the pool contract.
    uniswap_v3_pair_abi (str): The ABI of the pool contract.

    Returns:
    str: "UniV3" if the pool belongs to Uniswap V3, "<contract_address>" otherwise.
    """
    w3 = Web3(Web3.HTTPProvider(node_url))
    v3_pair_address = Web3.to_checksum_address(v3_pair_address)
    dex_contract = w3.eth.contract(address=v3_pair_address, abi=uniswap_v3_pair_abi)
    dex_address = dex_contract.functions.factory().call()

    if dex_address == constants.UNISWAP_V3_FACTORY_ADDRESS:
        dex_symbol = "UniV3"
    else:
        dex_symbol = dex_address
    return dex_symbol


########################################################################################
# Uniswp v3 check functions
########################################################################################
def has_uniswap_v3_swap_event(topics_0):
    """
    Check if the transaction has a Uniswap v3 swap event.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v3 swap event is present, False otherwise.
    """
    uniswap_v3_swap_event = constants.UNISWAP_V3_SWAP_EVENT
    return uniswap_v3_swap_event in topics_0


def has_uniswap_v3_mint_event(topics_0):
    """
    Check if the transaction has a Uniswap v3 mint event.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v3 mint event is present, False otherwise.
    """
    uniswap_v3_mint_event = constants.UNISWAP_V3_MINT_EVENT
    return uniswap_v3_mint_event in topics_0


def has_uniswap_v3_burn_event(topics_0):
    """
    Check if the transaction has a Uniswap v3 burn event.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v3 burn event is present, False otherwise.
    """
    uniswap_v3_burn_event = constants.UNISWAP_V3_BURN_EVENT
    return uniswap_v3_burn_event in topics_0
