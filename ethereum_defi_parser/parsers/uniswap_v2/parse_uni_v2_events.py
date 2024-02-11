"""
This file contains the parser for Unsiwap v2 events.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/ethereum-defi-parser
"""

# Import packages
import logging
from dataclasses import dataclass, field
from typing import Optional
from web3 import Web3


# Import modules
from ethereum_defi_parser.shared import constants, general_helpers, uniswap_v2_parsing
from ethereum_defi_parser.shared.general_classes import DexEvent

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# Define a base event class for Uniswap v2 events
########################################################################################


########################################################################################
# Parse all Uniswap v2 swaps, mints, and burns from a transaction
########################################################################################
def parse_all_v2_events(
    logs, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi, exchange_pair_address=""
):
    """Parse all swaps, mints, and burns from a tx.
    Args:
        logs (dict): Logs from a transaction's receipt.
        erc20_abi (dict): ERC-20 ABI
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi (dict): Uniswap v2 pair ABI
        exchange_pair_address (str): Exchange pair smart contract address that you want
        to match
    Returns:
        list: Containing lists of all parsed events
    """
    events = []

    # Get the first topic for all events in the logs
    topics_0 = general_helpers.get_topics_0(logs)

    # Get event hashes
    swap_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V2_SWAP_EVENT
    )
    mint_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V2_MINT_EVENT
    )
    burn_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V2_BURN_EVENT
    )

    # Convert exchange_pair_address to checksum
    if exchange_pair_address:
        try:
            exchange_pair_address = Web3.to_checksum_address(exchange_pair_address)
        except ValueError as e:
            logger.error(e, exc_info=True)

    # Parse swaps
    if swap_indexes:  # If the list is not empty
        if exchange_pair_address == "":
            swaps = parse_v2_trades(
                logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
            )
            for swap in swaps:
                if swap is not None:  # Since parse_trade(s) can return None
                    events.append(swap)
        else:
            for swap_index in swap_indexes:
                smart_contract = Web3.to_checksum_address(logs[swap_index]["address"])
                if smart_contract == exchange_pair_address:
                    swap = parse_v2_trade(
                        logs,
                        swap_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v2_pair_abi,
                    )
                    if swap is not None:
                        events.append(swap)

    # Parse mints
    if mint_indexes:
        if exchange_pair_address == "":
            mints = parse_v2_mints(
                logs, mint_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
            )
            for mint in mints:
                if mint is not None:
                    events.append(mint)
        else:
            for mint_index in mint_indexes:
                smart_contract = Web3.to_checksum_address(logs[mint_index]["address"])
                if smart_contract == exchange_pair_address:
                    mint = parse_v2_mint(
                        logs,
                        mint_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v2_pair_abi,
                    )
                    if mint is not None:
                        events.append(mint)

    # Parse burns
    if burn_indexes:
        if exchange_pair_address == "":
            burns = parse_v2_burns(
                logs, burn_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
            )
            for burn in burns:
                if burn is not None:
                    events.append(burn)
        else:
            for burn_index in burn_indexes:
                smart_contract = Web3.to_checksum_address(logs[burn_index]["address"])
                if smart_contract == exchange_pair_address:
                    burn = parse_v2_burn(
                        logs,
                        burn_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v2_pair_abi,
                    )
                    if burn is not None:
                        events.append(burn)

    return events


########################################################################################
# Trade parse functions
########################################################################################
def parse_v2_trades(
    logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
):
    """
    Parse all v2 trades of the tx by identifying all swap events and parse them.

    Args:
        swap_indexes: Index of where the swap event occur in the logs, e.g., [4, 7]
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
    """
    trades = []
    for swap_index in swap_indexes:
        trade = parse_v2_trade(
            logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
        )
        trades.append(trade)

    return trades


def parse_v2_trade(logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi):
    """
    Parse a Uniswap v2 swap event.
    Args:
        logs: Logs from receipt of transaction.
        swap_index: An index of where in the logs the swap event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    # Check that the event prior to the swap event is a sync event and that the events
    # have the same address in the logs.
    if not uniswap_v2_parsing.sync_event_is_before_event(logs, swap_index):
        transaction_hash = logs[swap_index]["transactionHash"]
        logger.error(
            "Sync event with same address not before swap event in tx: %s",
            transaction_hash,
            exc_info=True,
        )
        return None

    sync_log = logs[swap_index - 1]  # sync event is just before swap event

    swap_contract = logs[swap_index]["address"]
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(
        swap_contract, uniswap_v2_pair_abi
    )
    dex_symbol = uniswap_v2_parsing.get_v2_dex(swap_contract, erc20_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect the swap amounts delta x_t and delta y_t
    swap_data = logs[swap_index]["data"][2:]  # 256 characters after removing 0x
    amount_0_in = int(swap_data[0:64], 16)  # amount of token0 spent (USDC)
    amount_1_in = int(swap_data[64:128], 16)  # amount of token1 spent (USDC)
    amount_0_out = int(swap_data[128:192], 16)  # amount of token0 received (USDC)
    amount_1_out = int(swap_data[192:256], 16)  # amount of token1 reveived (USDC)

    # Calculate the "net traded amounts"
    dxt = amount_0_in - amount_0_out  # change in xt (USDC liquidity pool at t)
    dyt = amount_1_in - amount_1_out  # change in yt (wETH liquidity pool at t)

    # Collect NEW exchange rate from the sync event.
    # "Sync: Emitted each time reserves are updated via mint, burn, swap, or sync.
    sync_data = sync_log["data"][2:]  # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    yt1 = int(sync_data[64:128], 16)

    # Transform to base values, e.g., USDC to whole dollars and wETH to whole ether
    xt1 = xt1 * 10**-decimals_0
    yt1 = yt1 * 10**-decimals_1
    dxt = dxt * 10**-decimals_0
    dyt = dyt * 10**-decimals_1

    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    trade = [
        "swap",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        dxt,
        dyt,
        xt1,
        yt1,
        pt1,
        kt1,
    ]

    return trade


########################################################################################
# Liquidity provision parse functions
########################################################################################
def parse_v2_mints(
    logs, mint_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
):
    """
    Parse all v2 mints of the tx by identifying all mint events and parse them.

    Args:
        mint_indexes: Index of where the mint event occur in the logs, e.g., [4, 7]
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
    """
    mints = []
    for mint_index in mint_indexes:
        mint = parse_v2_mint(
            logs, mint_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
        )
        mints.append(mint)

    return mints


def parse_v2_mint(logs, mint_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi):
    """
    Parse a Uniswap v2 mint event (deposit liquidity).

    Arbs:
        logs: Logs from receipt of transaction.
        mint_index: An index of where in the logs the mint event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    # Check that the event prior to the mint event is a sync event and that the events
    # have the same address in the logs.
    if not uniswap_v2_parsing.sync_event_is_before_event(logs, mint_index):
        transaction_hash = logs[mint_index]["transactionHash"]

        logger.error(
            "Sync event with same address not before mint event in tx: %s",
            transaction_hash,
            exc_info=True,
        )
        return None

    sync_log = logs[mint_index - 1]  # sync event is just before mint event

    mint_contract = logs[mint_index]["address"]
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(
        mint_contract, uniswap_v2_pair_abi
    )
    dex_symbol = uniswap_v2_parsing.get_v2_dex(mint_contract, erc20_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect how much was deposited
    mint_data = logs[mint_index]["data"][2:]  # len 128
    dxt = int(mint_data[0:64], 16)  # amount of token0 deposited (USDC)
    dyt = int(mint_data[64:128], 16)  # amount of token1 deposited (USDC)

    # Collect NEW exchange rate from the sync event (are the same for LPing).
    # "Sync: Emitted each time reserves are updated via mint, mint, swap, or sync.
    sync_data = sync_log["data"][2:]  # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    yt1 = int(sync_data[64:128], 16)

    # Transform to base values
    xt1 = xt1 * 10**-decimals_0
    yt1 = yt1 * 10**-decimals_1
    dxt = dxt * 10**-decimals_0
    dyt = dyt * 10**-decimals_1

    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    mint = [
        "mint",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        dxt,
        dyt,
        xt1,
        yt1,
        pt1,
        kt1,
    ]

    return mint


def parse_v2_burns(
    logs, burn_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
):
    """
    Parse all v2 burns of the tx by identifying all burn events and parse them.

    Args:
        burn_indexes: Index of where the burn event occur in the logs, e.g., [4, 7]
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
    """
    burns = []
    for burn_index in burn_indexes:
        burn = parse_v2_burn(
            logs, burn_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
        )
        burns.append(burn)

    return burns


def parse_v2_burn(logs, burn_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi):
    """
    Parse a Uniswap v2 burn event (withdraw liquidity).

    Args:
        logs: Logs from receipt of transaction.
        burn_index: An index of where in the logs the burn event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    # Check that event[burn -1] is sync AND
    # Check that sync and burn have same address from logs
    if not uniswap_v2_parsing.sync_event_is_before_event(logs, burn_index):
        transaction_hash = logs[burn_index]["transactionHash"]

        logger.error(
            "Sync event with same address not before burn event in tx: %s",
            transaction_hash,
            exc_info=True,
        )
        return None

    sync_log = logs[burn_index - 1]  # sync event is just before burn event

    burn_contract = logs[burn_index]["address"]
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(
        burn_contract, uniswap_v2_pair_abi
    )
    dex_symbol = uniswap_v2_parsing.get_v2_dex(burn_contract, erc20_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect how much was burnt
    burn_data = logs[burn_index]["data"][2:]  # len 128
    dxt = -int(burn_data[0:64], 16)  # amount of token0 withdrawn (USDC)
    dyt = -int(burn_data[64:128], 16)  # amount of token1 withdrawn (USDC)

    # Collect NEW exchange rate from the sync event (are the same for LPing).
    # "Sync: Emitted each time reserves are updated via mint, burn, swap, or sync.
    sync_data = sync_log["data"][2:]  # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    yt1 = int(sync_data[64:128], 16)

    # Transform to base values
    xt1 = xt1 * 10**-decimals_0
    yt1 = yt1 * 10**-decimals_1
    dxt = dxt * 10**-decimals_0
    dyt = dyt * 10**-decimals_1

    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    burn = [
        "burn",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        dxt,
        dyt,
        xt1,
        yt1,
        pt1,
        kt1,
    ]

    return burn
