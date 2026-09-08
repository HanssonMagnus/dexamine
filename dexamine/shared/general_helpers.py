"""
This file contains general helper functions.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from typing import Any
import logging
import csv
from io import StringIO
import json
from importlib import resources
import requests
from web3 import Web3

# Import modules
from dexamine.shared import constants
from dexamine.shared.general_classes import EthereumToType

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# RPC call functions
########################################################################################
def get_tx_receipt_block_by_index(
    *, node_url: str, block_hex: str, index_hex: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Get tx, receipt, and block response from node.

    Args:
        block_hex (str): Hex of block number.
        index_hex (str): Hex of transaction index in block.

    Returns:
        tuple (dict, dict, dict): Transaction, receipt, and block data.

    """
    tx_data = get_tx_data_by_block_and_index(
        node_url=node_url, block_hex=block_hex, index_hex=index_hex
    )
    tx_hash = tx_data["hash"]
    receipt_data = get_receipt_data_by_hash(node_url=node_url, tx_hash=tx_hash)
    block_data = get_block_data_by_block_number(node_url=node_url, block_hex=block_hex)
    return tx_data, receipt_data, block_data


def get_tx_data_by_hash(*, node_url: str, tx_hash: str) -> dict[str, Any]:
    """
    Get tx response from node.

    Args:
        tx_hash (str): Transaction hash.

    Returns:
        dict: JSON dict object of transation data.

    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1,
    }
    timeout_seconds = 10
    res_tx = requests.post(
        node_url, headers=headers, json=payload, timeout=timeout_seconds
    )
    tx_data = res_tx.json()["result"]
    return tx_data


def get_tx_data_by_block_and_index(
    *, node_url: str, block_hex: str, index_hex: str
) -> dict[str, Any]:
    """Get tx response from node."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByBlockNumberAndIndex",
        "params": [block_hex, index_hex],
        "id": 1,
    }
    timeout_seconds = 10
    res_tx = requests.post(
        node_url, headers=headers, json=payload, timeout=timeout_seconds
    )
    tx_data = res_tx.json()["result"]
    return tx_data


def get_receipt_data_by_hash(*, node_url: str, tx_hash: str) -> dict[str, Any]:
    """Get receipt response from node."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx_hash],
        "id": 1,
    }
    timeout_seconds = 10
    res_receipt = requests.post(
        node_url, headers=headers, json=payload, timeout=timeout_seconds
    )
    receipt_data = res_receipt.json()["result"]
    return receipt_data


def get_block_data_by_block_number(*, node_url: str, block_hex: str) -> dict[str, Any]:
    """Get block response from node."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_hex, False],
        "id": 1,
    }
    timeout_seconds = 10
    res_block = requests.post(
        node_url, headers=headers, json=payload, timeout=timeout_seconds
    )
    block_data = res_block.json()["result"]
    return block_data


########################################################################################
# ABI call functions
########################################################################################
def get_erc20_symbol(
    *,
    node_url: str,
    token_address: str,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
) -> tuple[str, int]:
    """
    Match an ERC-20 token smart contract address to its symbol and get the number of
    decimals for that ERC-20 token.

    Args:
        token_address (str): Smart contract address of ERC-20 token.
        erc20_abi (dict): ERC-20 ABI.
        erc20_bytes32_abi (dict): ERC-20 ABI with Bytes32 type for symbol (some
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
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
    except OverflowError as e:  # some tokens return symbol as bytes32
        logger.error(e, exc_info=True)
        token_contract = w3.eth.contract(address=token_address, abi=erc20_bytes32_abi)
        symbol = token_contract.functions.symbol().call()
        symbol = bytes32_to_string(symbol)
        decimals = token_contract.functions.decimals().call()

    return symbol, decimals


########################################################################################
# Parsing transaction logs
########################################################################################
# def get_topics_0(logs: list[dict[str, Any]]) -> list:
#    """Return list of all "topic 0"s in logs."""
#    topics_0 = []
#    for log in logs:
#        # Check if 'topics' key exists and it has at least one element
#        if "topics" in log and len(log["topics"]) > 0:
#            topics_0.append(log["topics"][0])
#        else:
#            continue  # continue loop to next log
#    return topics_0


def get_topics_0(logs: list[dict[str, Any]]) -> list:
    """Return list of all 'topic 0's in logs, or an empty string if no topics are present."""
    topics_0 = []
    for log in logs:
        # If 'topics' key exists and has at least one element, append the first topic
        if "topics" in log and len(log["topics"]) > 0:
            topics_0.append(log["topics"][0])
        else:
            # Append an empty string if 'topics' is missing or empty
            topics_0.append("")
    return topics_0


def get_event_indexes(topics_0: list, events: list) -> list:
    """Returns: list, index of where in topics_0 the "event" occurs."""
    event_indexes = []
    for i, topic in enumerate(topics_0):
        if topic in events:
            event_indexes.append(i)
    return event_indexes


# THIS FUNCTION SHOULD BE REPLACED BY THE ONE ABOVE FOR ALL OCCURANCES
# def get_event_index(topics_0: list, event: str) -> list:
#    """Returns: list, index of where in topics_0 the "event" occurs."""
#    event_index = []
#    for i, topic in enumerate(topics_0):
#        if topic == event:
#            event_index.append(i)
#    return event_index


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
# Loading files
# Am I actually using these still? I think that they will be replaced by load resources
# files below.
########################################################################################
def load_json(path_json: str) -> dict:
    """Load a JSON file, e.g., a dictionary with blockNumber as key and txIndex as
    values."""
    with open(path_json, "r", encoding="utf-8") as file:
        return json.load(file)


def load_txt(file_path):
    """Yields generator object of a `.txt` file, one stripped line at a time."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()


def load_list(file_path):
    """Load a `.txt` file as a list."""
    gen_obj = load_txt(file_path)
    return list(gen_obj)


def load_abi(path_abi):
    """Load an ABI as a json object."""
    with open(path_abi, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["abi"]  # How they are constructed in this repo


########################################################################################
# Load resource files
########################################################################################
def get_json_test_data(test_data_file: str) -> dict:
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
        # with resources.open_text(resource_path, file_name) as file:
        return json.load(file)


def get_json_abi(abi_file: str) -> dict:
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
        return json.load(file)["abi"]


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
) -> dict:
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

    The function does not return any value. Instead, it writes the filtered data to the
    specified output file. It assumes that block numbers are represented as integers and
    are unique keys in the JSON structure.

    Example:
        filter_blocks('path_to_input.json', 'path_to_output.json', 12377035, 12377530)
    """
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    filtered_data = {
        block: txs
        for block, txs in data.items()
        if start_block <= int(block) <= end_block
    }

    with open(output_file, "w+", encoding="utf-8") as file:
        json.dump(filtered_data, file, indent=4)
