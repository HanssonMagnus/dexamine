"""
This file contains helper functions for parsers.uniswap_v2.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/ethereum-defi-parser
"""

# Import packages
from web3 import Web3

# Import modules
from ethereum_defi_parser.shared import constants

########################################################################################
# Uniswap v2 ABI call node functions
########################################################################################
def get_v2_pair(v2_pair_address, uniswap_v2_pair_abi):
    """Get meta data for an v2 pair from node."""
    url = constants.NODE_URL
    w3 = Web3(Web3.HTTPProvider(url))
    v2_pair_address = Web3.to_checksum_address(v2_pair_address)
    swap_contract = w3.eth.contract(address=v2_pair_address, abi=uniswap_v2_pair_abi)
    token0 = swap_contract.functions.token0().call()
    token1 = swap_contract.functions.token1().call()
    return token0, token1


def get_v2_dex(v2_pair_address, uniswap_v2_erc20_abi):
    """Get meta data for an v2 DEX from node."""
    url = constants.NODE_URL
    w3 = Web3(Web3.HTTPProvider(url))
    v2_pair_address = Web3.to_checksum_address(v2_pair_address)
    dex_contract = w3.eth.contract(address=v2_pair_address, abi=uniswap_v2_erc20_abi)
    dex_symbol = dex_contract.functions.symbol().call()
    return dex_symbol


########################################################################################
# Uniswp v2 check functions
########################################################################################
def has_uniswap_v2_swap_event(topics_0):
    """
    Check if the transaction has a Uniswap v2 swap event.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v2 swap event is present, False otherwise.
    """
    uniswap_v2_swap_event = constants.UNISWAP_V2_SWAP_EVENT
    return uniswap_v2_swap_event in topics_0


def has_uniswap_v2_burn_event(topics_0):
    """
    Check if the transaction has a Uniswap v2 burn event for removing liquidity.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v2 burn event is present, False otherwise.
    """
    uniswap_v2_burn_event = constants.UNISWAP_V2_BURN_EVENT
    return uniswap_v2_burn_event in topics_0


def has_uniswap_v2_mint_event(topics_0):
    """
    Check if the tx has a Uniswap v2 mint event for liquidity provision.

    Args:
        topics_0 (list): List of topics 0s.

    Returns:
        bool: True if the Uniswap v2 mint event is present, False otherwise.
    """
    uniswap_v2_mint_event = constants.UNISWAP_V2_MINT_EVENT
    return uniswap_v2_mint_event in topics_0

def sync_event_is_before_event(logs, event_index):
    """
    Check that the event prior to the swap/mint/burn event is a sync event and that the
    events have the same address in the logs.

    Args:
        logs (dict): Logs of the transaction.
        event_index (int): Index of the swap/mint/burn event in the logs.

    Returns:
        boolean: True or False.
    """
    if event_index == 0 or not (
        logs[event_index]["address"] == logs[event_index - 1]["address"]
        and logs[event_index - 1]["topics"][0] == constants.UNISWAP_V2_SYNC_EVENT
    ):
        transaction_hash = logs[swap_index]["transactionHash"]
        logger.error(
            f"Sync event with same address not before swap event in tx: {transaction_hash}",
            exc_info=True,
        )
        return False

    else:
        return True
