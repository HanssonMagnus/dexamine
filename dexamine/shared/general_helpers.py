"""
This file contains general helper functions.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from typing import Any, cast
import logging
import csv
from io import StringIO
import json
from importlib import resources
from web3 import Web3

# Import modules
from dexamine.shared import constants
from dexamine.shared.general_classes import EthereumToType

# A contract ABI as loaded from the JSON files in dexamine/resources/abis.
Abi = list[dict[str, Any]]

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# ABI call functions
########################################################################################
def get_erc20_symbol(
    *,
    node_url: str,
    token_address: str,
    erc20_abi: Abi,
    erc20_bytes32_abi: Abi,
) -> tuple[str, int]:
    """
    Match an ERC-20 token smart contract address to its symbol and get the number of
    decimals for that ERC-20 token.

    Args:
        token_address (str): Smart contract address of ERC-20 token.
        erc20_abi (Abi): ERC-20 ABI.
        erc20_bytes32_abi (Abi): ERC-20 ABI with Bytes32 type for symbol (some
                                 contracts have this to save gas).

    Returns:
        tuple (str, int): Symbol and number of decimals of the ERC-20 token.
    """
    # Transform address to checksum address
    token_address = Web3.to_checksum_address(token_address)
    try:
        w3 = Web3(Web3.HTTPProvider(node_url))
        token_address = Web3.to_checksum_address(token_address)
        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
        symbol = cast(str, token_contract.functions.symbol().call())
        decimals = cast(int, token_contract.functions.decimals().call())
    except OverflowError as e:  # some tokens return symbol as bytes32
        logger.error(e, exc_info=True)
        token_contract = w3.eth.contract(address=token_address, abi=erc20_bytes32_abi)
        symbol = bytes32_to_string(token_contract.functions.symbol().call())
        decimals = cast(int, token_contract.functions.decimals().call())

    return symbol, decimals


########################################################################################
# Parsing transaction logs
########################################################################################
def get_topics_0(logs: list[dict[str, Any]]) -> list[str]:
    """Return list of all 'topic 0's in logs, or an empty string if no topics are present."""
    topics_0: list[str] = []
    for log in logs:
        # If 'topics' key exists and has at least one element, append the first topic
        if "topics" in log and len(log["topics"]) > 0:
            topics_0.append(log["topics"][0])
        else:
            # Append an empty string if 'topics' is missing or empty
            topics_0.append("")
    return topics_0


def get_event_indexes(topics_0: list[str], events: list[str]) -> list[int]:
    """Returns: list, index of where in topics_0 the "event" occurs."""
    event_indexes: list[int] = []
    for i, topic in enumerate(topics_0):
        if topic in events:
            event_indexes.append(i)
    return event_indexes


########################################################################################
# Bytes32 parsing
########################################################################################
def bytes32_to_string(bytes32: bytes) -> str:
    """Decode using utf-8 and then strip the null characters."""
    return bytes32.decode("utf-8").rstrip("\x00")


########################################################################################
# Ethereum address parsing
########################################################################################
def normalize_eth_address(address: str) -> str:
    """
    Normalize Ethereum address by ensuring it's 40 characters long, excluding '0x'.
    """
    if address.startswith("0x"):
        # Strip the '0x', then remove leading zeros
        stripped_address = address[2:].lstrip("0")
        # Ensure address has 40 characters, padding with 0s at the start if necessary
        normalized_address = "0x" + stripped_address.rjust(40, "0")
        return normalized_address
    return address  # Return the original address if it doesn't start with '0x'


########################################################################################
# Hexadecimal parsing
########################################################################################
def parse_signed_int(hex_str: str) -> int:
    """
    Parses a hexadecimal string representing a signed integer in two's complement
    format.

    In Ethereum logs, integers are represented in two's complement format. This function
    converts a hexadecimal string to a signed integer. If the number is negative, it
    adjusts the value based on two's complement representation.

    Parameters:
    hex_str (str): A hexadecimal string representing a signed integer. The string should
                   not have '0x' at the beginning and should be 64 characters long (32
                   bytes).

    Returns:
    int: The signed integer value represented by the input hexadecimal string.

    Example:
    >>> parse_signed_int('FFFFFFFFFFFFFFFF...FFFFFFFFFFFFFFFFFFFFFFFFFFFFE')
    -2
    >>> parse_signed_int('0000000000000000...00000000000000000000000000001')
    1
    """
    value = int(hex_str, 16)
    if value >= 2**255:  # Check if the value is negative
        value -= 2**256
    return value


########################################################################################
# Parse transaction type from to address
########################################################################################
def parse_to_type(to_address: str | None) -> str:
    """
    Classify the route a transaction took before reaching a Uniswap pool.

    The classification uses one input only: the transaction `to` address, matched
    against the canonical Uniswap deployments in `constants.uniswap_address_list`.
    No curated third-party label data (for example Etherscan account labels) is
    used, so the output is deterministic and does not decay over time.

    Parameters:
    to_address (str | None): Ethereum transaction `to` address, or None.

    Returns:
    str: one of
        - 'uniswap_router': sent directly to a canonical Uniswap router or
          periphery contract,
        - 'other_contract': routed through any other contract (aggregator,
          arbitrage bot, or other DeFi protocol),
        - 'contract_creation': `to_address` is None.

    Note:
    A `to_address` that is not a valid hexadecimal address is logged and falls
    through to 'other_contract' rather than raising, so that callers can pass
    values straight from a node response without pre-validation.
    """
    if to_address is None:
        return EthereumToType.CONTRACT_CREATION.value

    # Transform HEX address to checksum address
    try:
        to_address = Web3.to_checksum_address(to_address)
    except ValueError as e:
        logger.error(e, exc_info=True)

    # Assign which route the transaction took to execution.
    if to_address in constants.uniswap_address_list:
        to_type = EthereumToType.UNISWAP_ROUTER.value
    else:
        to_type = EthereumToType.OTHER_CONTRACT.value

    return to_type


########################################################################################
# Load resource files
########################################################################################
def get_json_test_data(test_data_file: str) -> dict[str, Any]:
    """
    Load a JSON test data file from dexamine/tests/test_data.

    The `test_data_file` argument should include the subdirectory and filename. For example,
    "uniswap_v2/myfile.json" or "uniswap_v3/anotherfile.json".

    Args:
        test_data_file (str): Relative path of test data file within the test_data directory,
                              including subdirectories if applicable.
    """
    # Dynamically construct the package path
    package_path = "dexamine.tests.test_data"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = test_data_file.split("/")

    # Construct the resource path by joining the package path with the relative file path
    resource_path = ".".join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with (
        resources.files(resource_path)
        .joinpath(file_name)
        .open("r", encoding="utf-8") as file
    ):
        data: dict[str, Any] = json.load(file)
    return data


def get_json_abi(abi_file: str) -> Abi:
    """
    Load an ABI as a JSON file from dexamine/resources/abis.

    The `abi_file` argument should include the subdirectory and filename. For example,
    "uniswap_v2/IUniswapV2Pair.json".

    The ABIs are structured such that we return abi['abi'].

    Args:
        abi_file (str): Relative path of ABI file within the abis directory.
    """
    # Dynamically construct the package path
    package_path = "dexamine.resources.abis"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = abi_file.split("/")

    # Construct the resource path by joining the package path with the relative file path
    resource_path = ".".join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with (
        resources.files(resource_path)
        .joinpath(file_name)
        .open("r", encoding="utf-8") as file
    ):
        abi: Abi = json.load(file)["abi"]
    return abi


def get_csv_test_data_as_string(test_data_file: str) -> str:
    """
    Load a CSV test data file as a string from dexamine/tests/test_data.

    The `test_data_file` argument should include the subdirectory and filename. E.g.,
    "uniswap_v2/myfile.csv" or "uniswap_v3/anotherfile.csv".

    Args:
        test_data_file (str): Relative path of test data file within the test_data
                              directory, including subdirectories if applicable.
    """
    # Dynamically construct the package path
    package_path = "dexamine.tests.test_data"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = test_data_file.split("/")

    # Construct the resource path by joining the package path with the relative file path
    resource_path = ".".join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with (
        resources.files(resource_path)
        .joinpath(file_name)
        .open("r", encoding="utf-8") as file
    ):
        return file.read()


########################################################################################
# Transforming files
########################################################################################
def chifra_csv_to_json(csv_content: str) -> dict[str, list[str]]:
    """
    Transforms CSV content with blockNumber and transactionIndex to a JSON-like dict
    with the block as the key and the transactionIndex as values for that block. 'chifra
    list' can return duplicates of transactions, and this transformation avoids that.

    Args:
        csv_content (str): CSV content as a string. Which can be read in, e.g., like:
            with open(path_input, mode='r', encoding='utf-8') as file:
                csv_content = file.read()

    Returns:
        dict: A dictionary with block numbers as keys and lists of transaction indices
        as values.
    """
    # Convert the CSV content string into a file-like object
    csv_file = StringIO(csv_content)

    # Use csv.reader to parse the file-like object
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # Skip the headers

    tx_dict: dict[str, list[str]] = {}
    for row in csv_reader:
        block_number, tx_index = row[0], row[1]
        try:
            if not tx_index in tx_dict[block_number]:
                tx_dict[block_number].append(tx_index)
        except KeyError:
            tx_dict[block_number] = []
            tx_dict[block_number].append(tx_index)
    return tx_dict


def filter_blocks(
    input_file: str, output_file: str, start_block: int, end_block: int
) -> dict[str, list[str]]:
    """
    This function reads a JSON file containing Ethereum blocks and their transactions,
    filters the blocks based on a specified range, and writes the filtered data to a new
    JSON file.

    Args:
    input_file (str): The path to the input JSON file containing Ethereum blocks and
                      transactions.
    output_file (str): The path where the filtered data will be written in JSON format.
    start_block (int): The starting block number (inclusive) of the range to filter.
    end_block (int): The ending block number (inclusive) of the range to filter.

    The filtered data is written to `output_file` and also returned. Block numbers are
    assumed to be unique keys in the JSON structure.

    Example:
        filter_blocks('path_to_input.json', 'path_to_output.json', 12377035, 12377530)
    """
    with open(input_file, "r", encoding="utf-8") as file:
        data: dict[str, list[str]] = json.load(file)

    filtered_data = {
        block: txs
        for block, txs in data.items()
        if start_block <= int(block) <= end_block
    }

    with open(output_file, "w+", encoding="utf-8") as file:
        json.dump(filtered_data, file, indent=4)

    return filtered_data
