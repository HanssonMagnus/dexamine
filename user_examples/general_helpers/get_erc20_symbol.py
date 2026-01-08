"""
* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import sys
import os
import json
from pprint import pprint

# Import scirpts
from dexamine.shared import general_helpers

# Maker with Bytes32 as "symbol:
# 0x4d4b520000000000000000000000000000000000000000000000000000000000
maker_address = "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"

usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

erc20_abi = general_helpers.get_json_abi("erc20/ERC20_abi.json")
erc20_bytes32_abi = general_helpers.get_json_abi("erc20/ERC20_bytes32_abi.json")

symbol, decimals = general_helpers.get_erc20_symbol(
    maker_address, erc20_abi, erc20_bytes32_abi
)

pprint(symbol)
pprint(decimals)
