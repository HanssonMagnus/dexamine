"""
This file contains the parser for Unsiwap v3 events.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import logging
from web3 import Web3

# Import modules
from dexamine.shared import constants, general_helpers, uniswap_v3_parsing

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# Parse all Uniswap v3 swap, mint, and burn events from a transaction
########################################################################################
def parse_all_v3_events(
    logs, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi, exchange_pair_address=""
):
    """Parse all Unsiwap v3 swaps, mints, and burns from a tx.
    Inputs:
        logs: Logs from transaction receipt.
        exchange_pair_address: string of the exchange pair smart contract address.
    """
    events = []

    # Get the first topic for all events in the logs
    topics_0 = general_helpers.get_topics_0(logs)

    # Get event hashes
    swap_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V3_SWAP_EVENT
    )
    mint_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V3_MINT_EVENT
    )
    burn_indexes = general_helpers.get_event_index(
        topics_0, constants.UNISWAP_V3_BURN_EVENT
    )

    # Return the function is no swap, mint, or burn events are found
    if not swap_indexes and not mint_indexes and not burn_indexes:
        return None

    # Load ABIs
    # erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
    # uniswap_v3_pair_abi = general_helpers.load_abi(constants.PATH_UNISWAP_V3_PAIR_ABI)

    # Convert exchange_pair_address to checksum
    if exchange_pair_address:
        try:
            exchange_pair_address = Web3.to_checksum_address(exchange_pair_address)
        except ValueError as e:
            logger.error(e, exc_info=True)

    # Parse swaps
    if swap_indexes:  # If the list is not empty
        if exchange_pair_address:  # If string is not empty
            for swap_index in swap_indexes:
                smart_contract = Web3.to_checksum_address(logs[swap_index]["address"])
                if smart_contract == exchange_pair_address:
                    swap = parse_v3_trade(
                        logs,
                        swap_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if swap is not None:  # Since parse_trade(s) can return None
                        events.append(swap)

        elif not exchange_pair_address:  # if string is empty, i.e., == ''
            # Parse all swaps regardless of exchange pair
            swaps = parse_v3_trades(
                logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for swap in swaps:
                if swap is not None:  # Since parse_trade(s) can return None
                    events.append(swap)

    # Parse mints
    if mint_indexes:
        if exchange_pair_address:
            for mint_index in mint_indexes:
                smart_contract = Web3.to_checksum_address(logs[mint_index]["address"])
                if smart_contract == exchange_pair_address:
                    mint = parse_v3_mint(
                        logs,
                        mint_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if mint is not None:
                        events.append(mint)

        elif not exchange_pair_address:
            # Parse all mints regardless of exchange pair
            mints = parse_v3_mints(
                logs, mint_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for mint in mints:
                if mint is not None:
                    events.append(mint)

    # Parse burns
    if burn_indexes:
        if exchange_pair_address:
            for burn_index in burn_indexes:
                smart_contract = Web3.to_checksum_address(logs[burn_index]["address"])
                if smart_contract == exchange_pair_address:
                    burn = parse_v3_burn(
                        logs,
                        burn_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if burn is not None:
                        events.append(burn)

        elif not exchange_pair_address:
            # Parse all burns regardless of exchange pair
            burns = parse_v3_burns(
                logs, burn_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for burn in burns:
                if burn is not None:
                    events.append(burn)

    return events


########################################################################################
# Trade (swap events) parse functions
########################################################################################
def parse_v3_trades(
    logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
):
    """Parse all v3 trades of the tx by identifying all swap events and parse them.
    Inpur arguments:
        swap_indexes: Index of where the swap event occur in the logs, e.g., [4, 7]
    """
    trades = []
    for swap_index in swap_indexes:

        trade = parse_v3_trade(
            logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if trade is not None:
            trades.append(trade)

    return trades


def parse_v3_trade(logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi):
    """
    Parse a Uniswap v3 swap event.
    Input arguments:
        logs: Logs from receipt of transaction.
        swap_index: An index of where in the logs the swap event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """
    # Collect meta data
    swap_contract = logs[swap_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        swap_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(swap_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect the swap amounts delta x_t and delta y_t
    swap_data = logs[swap_index]["data"][2:]
    amount0 = general_helpers.parse_signed_int(
        swap_data[0:64]
    )  # pool change in token0 (- if pool sends out)
    amount1 = general_helpers.parse_signed_int(
        swap_data[64:128]
    )  # pool change in token1
    sqrt_price_x96 = int(swap_data[128:192], 16)  # mid-price of the pool after the swap
    liquidity = int(swap_data[192:256], 16)  # liquidity of pool after the swap
    tick = general_helpers.parse_signed_int(
        swap_data[256:320]
    )  # tick after the swap was executed

    # Transform amount0 and amount1 to base units
    amount0 = amount0 * 10**-decimals_0
    amount1 = amount1 * 10**-decimals_1

    # New exchange rate/price after the swap
    price = uniswap_v3_parsing.sqrt_price_x96_to_price(
        sqrt_price_x96, decimals_0, decimals_1
    )

    # Adding 'NA' for tick_lower and tick_upper for the mint/burn events
    trade = [
        "swap",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        amount0,
        amount1,
        liquidity,
        tick,
        sqrt_price_x96,
        price,
        "NA",
        "NA",
    ]

    return trade


########################################################################################
# Liquidity provision (mint and burn events) parse functions
########################################################################################
def parse_v3_mints(logs, mint_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi):
    """Parse all v3 mints of the tx by identifying all mint events and parse them.
    Inpur arguments:
        mint_indexes: Index of where the mint event occur in the logs, e.g., [4, 7]
    """
    mints = []
    for mint_index in mint_indexes:
        mint = parse_v3_mint(
            logs, mint_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if mint is not None:
            mints.append(mint)

    return mints


def parse_v3_mint(logs, mint_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi):
    """
    Parse a Uniswap v3 mint event (deposit liquidity).
    Input arguments:
        logs: Logs from receipt of transaction.
        mint_index: An index of where in the logs the mint event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    mint_contract = logs[mint_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        mint_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(mint_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect tick_lower and tick_upper
    tick_lower = general_helpers.parse_signed_int(logs[mint_index]["topics"][2])
    tick_upper = general_helpers.parse_signed_int(logs[mint_index]["topics"][3])

    # Collect how much was deposited
    mint_data = logs[mint_index]["data"][2:]  # len 128
    # sender = mint_data[24:64]  # Sender's address
    liquidity = int(mint_data[64:128], 16)  # Liquidity amount
    amount0 = int(mint_data[128:192], 16)  # Amount of token0
    amount1 = int(mint_data[192:256], 16)  # Amount of token1

    # Transform amount0 and amount1 to base units
    amount0 = amount0 * 10**-decimals_0
    amount1 = amount1 * 10**-decimals_1

    # Convert sender to Ethereum address format
    # sender_address = f"0x{sender}"

    mint = [
        "mint",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        amount0,
        amount1,
        liquidity,
        "NA",
        "NA",
        "NA",
        tick_lower,
        tick_upper,
    ]

    return mint


def parse_v3_burns(
    logs, burn_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
):
    """Parse all v3 burns of the tx by identifying all burn events and parse them.
    Inpur arguments:
        burn_indexes: Index of where the burn event occur in the logs, e.g., [4, 7]
    """
    burns = []
    for burn_index in burn_indexes:
        burn = parse_v3_burn(
            logs, burn_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if burn is not None:
            burns.append(burn)

    return burns


def parse_v3_burn(logs, burn_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi):
    """
    Parse a Uniswap v2 burn event (deposit liquidity).
    Input arguments:
        logs: Logs from receipt of transaction.
        burn_index: An index of where in the logs the burn event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    burn_contract = logs[burn_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        burn_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(burn_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect tick_lower and tick_upper
    tick_lower = general_helpers.parse_signed_int(logs[burn_index]["topics"][2])
    tick_upper = general_helpers.parse_signed_int(logs[burn_index]["topics"][3])

    # Collect how much was deposited
    burn_data = logs[burn_index]["data"][2:]  # len 128
    liquidity = int(burn_data[0:64], 16)  # Liquidity amount
    amount0 = -int(
        burn_data[64:128], 16
    )  # Amount of token0 (set as negative, since out of pool)
    amount1 = -int(
        burn_data[128:192], 16
    )  # Amount of token1 (set as negative, since out of pool)

    # Transform amount0 and amount1 to base units
    amount0 = amount0 * 10**-decimals_0
    amount1 = amount1 * 10**-decimals_1

    burn = [
        "burn",
        dex_symbol,
        symbol_0,
        symbol_1,
        decimals_0,
        decimals_1,
        amount0,
        amount1,
        liquidity,
        "NA",
        "NA",
        "NA",
        tick_lower,
        tick_upper,
    ]

    return burn
