"""
This file contains unit tests for the classes in dexamine/shared/general_classes.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from unittest.mock import mock_open, patch
import importlib.resources as pkg_resources
import pytest

# Import modules
from dexamine.shared.general_classes import DexEvent, DexEventType, EthereumToType


########################################################################################
# Test for DexEvent
########################################################################################
# Test for normal initialization and attribute access
def test_dex_event_initialization():
    dex_event = DexEvent("UNI", "ETH", "USDT", 18, 6, 10)
    assert dex_event.dex_symbol == "UNI"
    assert dex_event.symbol_0 == "ETH"
    assert dex_event.symbol_1 == "USDT"
    assert dex_event.decimals_0 == 18
    assert dex_event.decimals_1 == 6
    assert dex_event.event_index == 10

# Test for transform_to_base with standard input
def test_transform_to_base_normal():
    assert DexEvent.transform_to_base(1000, 2) == 10

# Test for transform_to_base with zero decimals
def test_transform_to_base_zero_decimals():
    assert DexEvent.transform_to_base(1000, 0) == 1000

# Test for transform_to_base with None amount
def test_transform_to_base_none_amount():
    with pytest.raises(ValueError):
        DexEvent.transform_to_base(None, 2)

# Test for transform_to_base with boundary conditions
@pytest.mark.parametrize("amount,decimals,expected", [
    (1e18, 18, 1),
    (1, 0, 1),
    (-1e18, 18, -1),
])
def test_transform_to_base_boundary_conditions(amount, decimals, expected):
    assert DexEvent.transform_to_base(amount, decimals) == expected

########################################################################################
# Test for DexEventType
########################################################################################
def test_dex_event_type_values():
    assert DexEventType.SWAP.value == "swap"
    assert DexEventType.MINT.value == "mint"
    assert DexEventType.BURN.value == "burn"

########################################################################################
# Test for EthereumToType
########################################################################################
def test_ethereum_to_type_values():
    assert EthereumToType.DEX_ROUTER.value == "dex_router"
    assert EthereumToType.SMART_CONTRACT.value == "smart_contract"
    assert EthereumToType.CONTRACT_CREATION.value == "contract_creation"
