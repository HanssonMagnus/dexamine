# This file contains general helper function.

# Import packages
import requests
import json
import csv
from web3 import Web3

# Import scirpts
from . import constants

###################################################################################################
# RPC call functions
###################################################################################################
def get_tx_receipt_block_by_index(block_hex, index_hex):
    '''Get tx, receipt, and block response from node.'''
    tx_data = get_tx_data_by_block_and_index(block_hex, index_hex)
    hash = tx_data['hash']
    receipt_data = get_receipt_data_by_hash(hash)
    block_data = get_block_data_by_block_number(block_hex)
    return tx_data, receipt_data, block_data


def get_tx_data_by_hash(hash):
    '''Get tx response from node.'''
    url = 'http://localhost:8545'
    headers = {'Content-Type': 'application/json'}
    payload = {'jsonrpc': '2.0',
               'method': 'eth_getTransactionByHash',
               'params': [hash],
               'id': 1}
    res_tx = requests.post(url, headers=headers, json=payload)
    tx_data = res_tx.json()['result']
    return tx_data

def get_tx_data_by_block_and_index(block_hex, index_hex):
    '''Get tx response from node.'''
    url = 'http://localhost:8545'
    headers = {'Content-Type': 'application/json'}
    payload = {'jsonrpc': '2.0',
               'method': 'eth_getTransactionByBlockNumberAndIndex',
               'params': [block_hex, index_hex],
               'id': 1}
    res_tx = requests.post(url, headers=headers, json=payload)
    tx_data = res_tx.json()['result']
    return tx_data

def get_receipt_data_by_hash(hash):
    '''Get receipt response from node.'''
    url = 'http://localhost:8545'
    headers = {'Content-Type': 'application/json'}
    payload = {'jsonrpc': '2.0',
               'method': 'eth_getTransactionReceipt',
               'params': [hash],
               'id': 1}
    res_receipt = requests.post(url, headers=headers, json=payload)
    receipt_data = res_receipt.json()['result']
    return receipt_data

def get_block_data_by_block_number(block_hex):
    '''Get block response from node.'''
    url = 'http://localhost:8545'
    headers = {'Content-Type': 'application/json'}
    payload = {'jsonrpc': '2.0',
               'method': 'eth_getBlockByNumber',
               'params': [block_hex, False],
               'id': 1}
    res_block = requests.post(url, headers=headers, json=payload)
    block_data = res_block.json()['result']
    return block_data

###################################################################################################
# ABI call functions
###################################################################################################
def get_erc20_symbol(token_address, erc20_abi):
    '''Match an ERC20 token smart contract address to its symbol.'''
    # Transform address to checksum address
    token_address = Web3.to_checksum_address(token_address)
    try:
        url = 'http://localhost:8545'
        w3 = Web3(Web3.HTTPProvider(url))
        token_address = Web3.to_checksum_address(token_address)
        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
    except Exception as e: # some tokens return symbol as bytes32
        logger.error(e, exc_info=True)
        symbol = "unknown"

    return symbol, decimals #string

###################################################################################################
# Parsing transaction logs
###################################################################################################
def get_topics_0(logs):
    '''Return list of all "topic 0"s in logs.'''
    topics_0 = []
    for log in logs:
        topics_0.append(log['topics'][0])
    return topics_0

def get_event_index(topics_0, event):
    '''Returns: list, index of where in topics_0 the "event" occurs.'''
    event_index = []
    for i in range(len(topics_0)):
        if topics_0[i] == event:
            event_index.append(i)
    return event_index

###################################################################################################
# Hexadecimal parsing
###################################################################################################
def parse_signed_int(hex_str):
    """
    Parses a hexadecimal string representing a signed integer in two's complement format.

    In Ethereum logs, integers are represented in two's complement format. This function
    converts a hexadecimal string to a signed integer. If the number is negative, it adjusts
    the value based on two's complement representation.

    Parameters:
    hex_str (str): A hexadecimal string representing a signed integer. The string should not
                   have '0x' at the beginning and should be 64 characters long (32 bytes).

    Returns:
    int: The signed integer value represented by the input hexadecimal string.

    Example:
    >>> parse_signed_int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE')
    -2
    >>> parse_signed_int('0000000000000000000000000000000000000000000000000000000000000001')
    1
    """
    value = int(hex_str, 16)
    if value >= 2**255:  # Check if the value is negative
        value -= 2**256
    return value

###################################################################################################
# Parse transaction type from to address
###################################################################################################
def parse_to_type(to_address, mev_contracts_list):
    # Transform address to checksum address
    to_address = Web3.to_checksum_address(to_address)

    # Assign which route the transaction took to execution.
    if to_address in mev_contracts_list:
        to_type = 'mev'
    elif to_address == constants.uniswap_v3_router_address:
        to_type = 'uni'
    elif to_address == constants.uniswap_v3_positions_nft_address:
        to_type = 'uni'
    elif to_address == constants.uniswap_universal_router_address:
        to_type = 'uni'
    elif to_address == constants.uniswap_v3_migrator_address:
        to_type = 'uni'
    elif to_address == constants.uniswap_v2_router_address:
        to_type = 'uni'
    else:
        to_type = 'defi'

    return to_type

###################################################################################################
# Loading files
###################################################################################################
def load_json(path_json):
    '''Load a JSON file, e.g., a dictionary with blockNumber as key and txIndex as values.'''
    with open(path_json, 'r') as file:
        return json.load(file)

def load_txt(file_path):
    '''Yields generator object of, e.g., mev_contracts.txt'''
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

def load_list(file_path):
    '''Load a txt as a list'''
    gen_obj = load_txt(file_path)
    return list(gen_obj)

def load_abi(path_abi):
    with open(path_abi, 'r') as file:
        data = json.load(file)
        return data['abi'] # how they are constructed

###################################################################################################
# Transforming files
###################################################################################################
def chifra_csv_to_json(csv_path):
    '''Transforms a csv with blockNumber and transactionIndex to a json file with the block as the
    key and the transationIndex as values for that block. chifra list can return duplicates of
    transactions.'''
    csv_file = open(csv_path, 'r')
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)  # Skip the headers
    tx_dict = {}
    for row in csv_reader:
        blockNumber = row[0]
        txIndex = row[1]
        try:
            if not txIndex in tx_dict[blockNumber]:
                tx_dict[blockNumber].append(txIndex)
        except KeyError:
            tx_dict[blockNumber] = []
            tx_dict[blockNumber].append(txIndex)
    csv_file.close()
    return tx_dict

def filter_blocks(input_file, output_file, start_block, end_block):
    """
    This function reads a JSON file containing Ethereum blocks and their transactions,
    filters the blocks based on a specified range, and writes the filtered data to a new JSON file.

    Parameters:
    input_file (str): The path to the input JSON file containing Ethereum blocks and transactions.
    output_file (str): The path where the filtered data will be written in JSON format.
    start_block (int): The starting block number (inclusive) of the range to filter.
    end_block (int): The ending block number (inclusive) of the range to filter.

    The function does not return any value. Instead, it writes the filtered data to the specified
    output file. It assumes that block numbers are represented as integers and are unique keys in
    the JSON structure.

    Example:
        filter_blocks('path_to_input.json', 'path_to_output.json', 12377035, 12377530)
    """
    with open(input_file, 'r') as file:
        data = json.load(file)

    filtered_data = {block: txs for block, txs in data.items() if start_block <= int(block) <= end_block}

    with open(output_file, 'w+') as file:
        json.dump(filtered_data, file, indent=4)
