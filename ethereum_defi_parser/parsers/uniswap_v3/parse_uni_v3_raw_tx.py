"""
This file contains the parser for raw transactions containing Unsiwap v3 swaps.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/ethereum-defi-parser
"""

# Import packages
import logging
from web3 import Web3
import eth_abi

# Import modules
from ethereum_defi_parser.shared import general_helpers

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# Raw data from signed transation (mempool) parse functions
########################################################################################
def parse_v3_exact_input_single(data, erc20_abi, token_in="", token_out=""):
    """
    Parse direct Uniswap v3 swap calls from exactInputSingle.

    exactInputSingle(...)
    - Parameters:
        - `tokenIn`: Address of the token being sent.
        - `tokenOut`: Address of the token being received.
        - `fee`: Fee tier of the pool.
        - `recipient`: Address receiving the output tokens.
        - `deadline`: Time after which the transaction will revert.
        - `amount_in`: Exact amount of `tokenIn` to swap.
        - `amount_out_minimum`: Minimum amount of `tokenOut` to receive.
        - `sqrt_price_limit_x96`: Limit on the pool's price movement.
    """
    if data == "0x":  # If there is no data in the tx
        return  # Returns None

    # Function signature for exactInputSingle
    sig_exact_input_single = "414bf389"

    # ABI Types for exactInputSingle
    abi_types = [
        "address",
        "address",
        "uint24",
        "address",
        "uint256",
        "uint256",
        "uint256",
        "uint160",
    ]

    swaps = []

    # Search for the first occurance of the signature in the data string
    pos = data.find(sig_exact_input_single)
    while pos != -1:  # Loop to handle multiple occurrences
        # Each parameter is 64 characters long in the data string
        # There are 8 parameters for exactInputSingle
        start = pos + len(sig_exact_input_single)
        end = start + 64 * len(abi_types)

        # Extract and decode the arguments
        encoded_args = data[start:end]
        decoded_args = eth_abi.decode(abi_types, bytes.fromhex(encoded_args))

        # Collect arguments
        token_in_address = decoded_args[0]
        token_out_address = decoded_args[1]

        # Check if token_in and token_out addresses are used in the function argument
        # and if they are match them.
        if not (token_in == "" and token_out == ""):
            token_in_address = Web3.to_checksum_address(token_in_address)
            token_out_address = Web3.to_checksum_address(token_out_address)
            if not (token_in_address == token_in and token_out_address == token_out):
                pos = data.find(sig_exact_input_single, end)
                continue

        fee = decoded_args[2]
        recipient = decoded_args[3]
        deadline = decoded_args[4]
        amount_in = decoded_args[5]
        amount_out_minimum = decoded_args[6]
        sqrt_price_limit_x96 = decoded_args[7]

        # Get symbols from tokens and transform values to base units
        try:
            symbol_in, decimals_in = general_helpers.get_erc20_symbol(
                token_in_address, erc20_abi
            )
            symbol_out, decimals_out = general_helpers.get_erc20_symbol(
                token_out_address, erc20_abi
            )

            amount_in = amount_in * 10**-decimals_in
            amount_out_minimum = amount_out_minimum * 10**-decimals_out
            limit_exchange_rate = amount_in / amount_out_minimum

        except Exception as e:
            logger.error(e, exc_info=True)

        # Append to swaps
        try:
            swaps.append(
                [
                    "exactInputSingle",
                    symbol_in,
                    symbol_out,
                    decimals_in,
                    decimals_out,
                    token_in_address,
                    token_out_address,
                    fee,
                    recipient,
                    deadline,
                    amount_in,
                    amount_out_minimum,
                    limit_exchange_rate,
                    sqrt_price_limit_x96,
                ]
            )
        except Exception as e:
            logger.error(e, exc_info=True)

        # Look for next occurrence, returns -1 if no occurance is found
        pos = data.find(sig_exact_input_single, end)

    return swaps


def parse_v3_exact_output_single(data, erc20_abi):
    """
    Parse direct Uniswap v3 swap calls from exactOutputSingle.

    exactOutputSingle(...)
    - Parameters:
        - `tokenIn`: Address of the token being sent.
        - `tokenOut`: Address of the token being received.
        - `fee`: Fee tier of the pool.
        - `recipient`: Address receiving the output tokens.
        - `deadline`: Time after which the transaction will revert.
        - `amount_out`: Exact amount of `tokenOut` to receive.
        - `amount_in_maximum`: Maximum amount of `tokenIn` to spend.
        - `sqrt_price_limit_x96`: Limit on the pool's price movement.
    """
    if data == "0x":  # If there is no data in the tx
        return  # Returns None

    # Function signature for exactOutputSingle
    sig_exact_output_single = "db3e2198"

    # ABI Types for exactInputSingle
    abi_types = [
        "address",
        "address",
        "uint24",
        "address",
        "uint256",
        "uint256",
        "uint256",
        "uint160",
    ]

    swaps = []

    # Search for the first occurance of the signature in the data string
    pos = data.find(sig_exact_output_single)
    while pos != -1:  # Loop to handle multiple occurrences
        # Each parameter is 64 characters long in the data string
        # There are 8 parameters for exact_output_single
        start = pos + len(sig_exact_output_single)
        end = start + 64 * len(abi_types)

        # Extract and decode the arguments
        encoded_args = data[start:end]
        decoded_args = eth_abi.decode(abi_types, bytes.fromhex(encoded_args))

        # Collect arguments
        token_in_address = decoded_args[0]
        token_out_address = decoded_args[1]
        fee = decoded_args[2]
        recipient = decoded_args[3]
        deadline = decoded_args[4]
        amount_out = decoded_args[5]
        amount_in_minimum = decoded_args[6]
        sqrt_price_limit_x96 = decoded_args[7]

        # Get symbols from tokens and transform values to base units
        try:
            symbol_in, decimals_in = general_helpers.get_erc20_symbol(
                token_in_address, erc20_abi
            )
            symbol_out, decimals_out = general_helpers.get_erc20_symbol(
                token_out_address, erc20_abi
            )

            amount_in_minimum = amount_in_minimum * 10**-decimals_in
            amount_out = amount_out * 10**-decimals_out
            limit_exchange_rate = amount_in_minimum / amount_out

        except Exception as e:
            logger.error(e, exc_info=True)

        # Append to swaps
        try:
            swaps.append(
                [
                    "exactOutputSingle",
                    symbol_in,
                    symbol_out,
                    decimals_in,
                    decimals_out,
                    token_in_address,
                    token_out_address,
                    fee,
                    recipient,
                    deadline,
                    amount_in_minimum,
                    amount_out,
                    limit_exchange_rate,
                    sqrt_price_limit_x96,
                ]
            )
        except Exception as e:
            logger.error(e, exc_info=True)

        # Look for next occurrence, returns -1 if no occurance is found
        pos = data.find(sig_exact_output_single, end)

    return swaps
