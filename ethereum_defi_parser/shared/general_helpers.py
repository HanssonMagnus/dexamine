"""
This file contains general helper functions.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/ethereum-defi-parser
"""

# Import packages
import logging
import csv
from io import StringIO
import json
from importlib import resources
import importlib.resources as pkg_resources
import requests
from web3 import Web3

# Import packages for mempool decoding
from eth.vm.forks.arrow_glacier.transactions import (
    ArrowGlacierTransactionBuilder as TransactionBuilder,
)
from eth_utils import encode_hex, to_bytes

# Import modules
from ethereum_defi_parser.shared import constants

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# RPC call functions
########################################################################################
def get_tx_receipt_block_by_index(block_hex, index_hex):
    """
    Get tx, receipt, and block response from node.

    Args:
        block_hex (str): Hex of block number.
        index_hex (str): Hex of transaction index in block.

    Returns:
        tuple (dict, dict, dict): Transaction, receipt, and block data.

    """
    tx_data = get_tx_data_by_block_and_index(block_hex, index_hex)
    tx_hash = tx_data["hash"]
    receipt_data = get_receipt_data_by_hash(tx_hash)
    block_data = get_block_data_by_block_number(block_hex)
    return tx_data, receipt_data, block_data


def get_tx_data_by_hash(tx_hash):
    """
    Get tx response from node.

    Args:
        tx_hash (str): Transaction hash.

    Returns:
        dict: JSON dict object of transation data.

    """
    url = constants.NODE_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1,
    }
    timeout_seconds = 10
    res_tx = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    tx_data = res_tx.json()["result"]
    return tx_data


def get_tx_data_by_block_and_index(block_hex, index_hex):
    """Get tx response from node."""
    url = constants.NODE_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByBlockNumberAndIndex",
        "params": [block_hex, index_hex],
        "id": 1,
    }
    timeout_seconds = 10
    res_tx = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    tx_data = res_tx.json()["result"]
    return tx_data


def get_receipt_data_by_hash(tx_hash):
    """Get receipt response from node."""
    url = constants.NODE_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx_hash],
        "id": 1,
    }
    timeout_seconds = 10
    res_receipt = requests.post(
        url, headers=headers, json=payload, timeout=timeout_seconds
    )
    receipt_data = res_receipt.json()["result"]
    return receipt_data


def get_block_data_by_block_number(block_hex):
    """Get block response from node."""
    url = constants.NODE_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_hex, False],
        "id": 1,
    }
    timeout_seconds = 10
    res_block = requests.post(
        url, headers=headers, json=payload, timeout=timeout_seconds
    )
    block_data = res_block.json()["result"]
    return block_data


########################################################################################
# ABI call functions
########################################################################################
def get_erc20_symbol(token_address, erc20_abi):
    """
    Match an ERC20 token smart contract address to its symbol.

    Args:
        token_address (str): Smart contract address of ERC-20 token
        erc20_abi (dict): ERC-20 ABI

    Returns:
        tuple (str, int): Symbol and number of decimals of ERC-20 token.
    """
    # Transform address to checksum address
    token_address = Web3.to_checksum_address(token_address)
    try:
        url = constants.NODE_URL
        w3 = Web3(Web3.HTTPProvider(url))
        token_address = Web3.to_checksum_address(token_address)
        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
    except Exception as e:  # some tokens return symbol as bytes32
        logger.error(e, exc_info=True)
        symbol = "unknown"

    return symbol, decimals  # string


########################################################################################
# Parsing transaction logs
########################################################################################
def get_topics_0(logs):
    """Return list of all "topic 0"s in logs."""
    topics_0 = []
    for log in logs:
        # Check if 'topics' key exists and it has at least one element
        if "topics" in log and len(log["topics"]) > 0:
            topics_0.append(log["topics"][0])
        else:
            continue  # continue loop to next log
    return topics_0


def get_event_index(topics_0, event):
    """Returns: list, index of where in topics_0 the "event" occurs."""
    event_index = []
    for i, topic in enumerate(topics_0):
        if topic == event:
            event_index.append(i)
    return event_index


########################################################################################
# Hexadecimal parsing
########################################################################################
def parse_signed_int(hex_str):
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
def parse_to_type(to_address, mev_contracts_list):
    """
    Parse the transaction to_address.

    Parameters:
    to_address (str): Ethereum transaction to address.
    mev_constracts_list (list): List of Ethereum address associated with MEV.

    Returns:
    str: 'uni', 'defi', or 'mev'

    Note:
    If to_address is None I set it to 'contract_creation' in the multiprocessing parse
    script. Ensure that 'contract_creation' strings will not raise ValueError as it is
    not a HEX string.
    """
    if to_address == "contract_creation":
        return "contract_creation"

    # Transform HEX address to checksum address
    try:
        to_address = Web3.to_checksum_address(to_address)
    except Exception as e:
        logger.error(e, exc_info=True)

    # Assign which route the transaction took to execution.
    if to_address in mev_contracts_list:
        to_type = "mev"
    elif to_address == constants.UNISWAP_V3_ROUTER_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_V3_POSITIONS_NFT_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_UNIVERSAL_ROUTER_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_V3_MIGRATOR_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_V2_ROUTER_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_V3_ROUTER_2_ADDRESS:
        to_type = "uni"
    elif to_address == constants.UNISWAP_V2_ROUTER_2_ADDRESS:
        to_type = "uni"
    else:
        to_type = "defi"

    return to_type


########################################################################################
# Decode raw transaction from mempool
########################################################################################
def decode_mempool_tx(raw_tx):
    """
    Decodes both EIP-1559 and Legacy Ethereum transactions.
    - 1559 tx: dict_keys(['type_id', '_inner'])
    - Legacy tx: dict_keys(['_nonce', '_gas_price', '_gas', '_to', '_value', '_data',
      '_v', '_r', '_s', '_cached_rlp'])

    Parameters:
    raw_tx (str): A hexadecimal string representing a signed transaction.

    Returns:
    dict: Decoded transaction.

    Mock example of raw_tx: '0xf86901844190ab00825208943 ... 9a0a414587d4b614d36a3f5b27'
    """
    # Convert the hex string to bytes
    signed_tx_as_bytes = to_bytes(hexstr=raw_tx)

    # Deserialize the transaction using the latest transaction builder:
    decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)

    # Transform to dict
    decoded_tx_dict = decoded_tx.__dict__

    # Check for transaction type and process accordingly
    if "type_id" in decoded_tx_dict:
        # EIP-1559 transaction
        decoded_tx_dict = decoded_tx_dict.get("_inner", {}).__dict__
    else:
        # Legacy transaction
        pass  # No special handling needed for legacy transactions

    # Common processing for both types
    if "_data" in decoded_tx_dict:
        decoded_tx_dict["_data"] = encode_hex(decoded_tx_dict["_data"])
    if "_cached_rlp" in decoded_tx_dict:
        decoded_tx_dict["_cached_rlp"] = encode_hex(decoded_tx_dict["_cached_rlp"])
    if "_to" in decoded_tx_dict:
        decoded_tx_dict["_to"] = encode_hex(decoded_tx_dict["_to"])

    return decoded_tx_dict


########################################################################################
# Loading files
########################################################################################
def load_json(path_json):
    """Load a JSON file, e.g., a dictionary with blockNumber as key and txIndex as
    values."""
    with open(path_json, "r", encoding="utf-8") as file:
        return json.load(file)


def load_txt(file_path):
    """Yields generator object of, e.g., mev_contracts.txt."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()


def load_list(file_path):
    """Load a txt as a list."""
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
def get_json_test_data(test_data_file):
    """
    Load a JSON test data file from ethereum_defi_parser/resources/test_data.

    The `test_data_file` argument should include the subdirectory and filename. For example,
    "uniswap_v2/myfile.json" or "uniswap_v3/anotherfile.json".

    Args:
        test_data_file (str): Relative path of test data file within the test_data directory,
                              including subdirectories if applicable.
    """
    # Dynamically construct the package path
    package_path = "ethereum_defi_parser.resources.test_data"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = test_data_file.split('/')

    # Construct the resource path by joining the package path with the relative file path
    resource_path = '.'.join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with resources.open_text(resource_path, file_name) as file:
        return json.load(file)

def get_json_abi(abi_file):
    """
    Load an ABI as a JSON file from ethereum_defi_parser/resources/abis.

    The `abi_file` argument should include the subdirectory and filename. For example,
    "uniswap_v2/IUniswapV2Pair.json".

    Args:
        abi_file (str): Relative path of ABI file within the abis directory.
    """
    # Dynamically construct the package path
    package_path = "ethereum_defi_parser.resources.abis"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = abi_file.split('/')

    # Construct the resource path by joining the package path with the relative file path
    resource_path = '.'.join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with resources.open_text(resource_path, file_name) as file:
        return json.load(file)


def get_txt_as_list(txt_file):
    """
    Load a .txt file as a list from ethereum_defi_parser/resources/lists.

    The `txt_file` argument should include the subdirectory and filename. For example,
    "mev_contracts.txt".

    Args:
        txt_file (str): Relative path of the .txt file within the lists directory.
    """
    # Dynamically construct the package path
    package_path = "ethereum_defi_parser.resources.lists"

    # Split the txt_file into components (subdirectories + filename)
    path_components = txt_file.split('/')

    # Construct resource path by joining the package path with the relative file path
    resource_path = '.'.join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use resources.open_text to access the file
    with resources.open_text(resource_path, file_name) as file:
        # Remove newline characters and skip empty lines
        return [line.strip() for line in file if line.strip()]


def get_csv_test_data_as_string(test_data_file):
    """
    Load a CSV test data file as a string from ethereum_defi_parser/resources/test_data.

    The `test_data_file` argument should include the subdirectory and filename. E.g.,
    "uniswap_v2/myfile.csv" or "uniswap_v3/anotherfile.csv".

    Args:
        test_data_file (str): Relative path of test data file within the test_data
                              directory, including subdirectories if applicable.
    """
    # Dynamically construct the package path
    package_path = "ethereum_defi_parser.resources.test_data"

    # Split the test_data_file into components (subdirectories + filename)
    path_components = test_data_file.split('/')

    # Construct the resource path by joining the package path with the relative file path
    resource_path = '.'.join([package_path] + path_components[:-1])
    file_name = path_components[-1]

    # Use pkg_resources.open_text to access the file
    with pkg_resources.open_text(resource_path, file_name) as file:
        return file.read()

########################################################################################
# Transforming files
########################################################################################
def chifra_csv_to_json(csv_content):
    """
    Transforms CSV content with blockNumber and transactionIndex to a JSON-like dict
    with the block as the key and the transactionIndex as values for that block. 'chifra
    list' can return duplicates of transactions, and this transformation avoids that.

    Args:
        csv_content (str): CSV content as a string.

    Returns:
        dict: A dictionary with block numbers as keys and lists of transaction indices
        as values.
    """
    # Convert the CSV content string into a file-like object
    csv_file = StringIO(csv_content)

    # Use csv.reader to parse the file-like object
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # Skip the headers

    tx_dict = {}
    for row in csv_reader:
        block_number, tx_index = row[0], row[1]
        try:
            if not tx_index in tx_dict[block_number]:
                tx_dict[block_number].append(tx_index)
        except KeyError:
            tx_dict[block_number] = []
            tx_dict[block_number].append(tx_index)
    return tx_dict

def filter_blocks(input_file, output_file, start_block, end_block):
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
