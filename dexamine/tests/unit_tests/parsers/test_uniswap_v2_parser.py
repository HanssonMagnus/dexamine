"""
This file contains unit tests for the classes and functions in
dexamine/parsers/uniswap_v2_parser.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import pytest

# Import modules
from dexamine.shared.general_classes import DexEventType
from dexamine.parsers.uniswap_v2_parser import (
    UniswapV2Event,
    UniswapV2Swap,
    UniswapV2Lp,
)
from dexamine.parsers import uniswap_v2_parser


########################################################################################
# Test for class UnsiwapV2Event
########################################################################################
def test_uniswap_v2_event_positive_reserves():
    """Test for UniswapV2Event class."""
    event = UniswapV2Event("UniswapV2", "USDC", "WETH", 6, 18, 10, 1000, 2000)
    assert event.reserve_0 > 0 and event.reserve_1 > 0
    assert event.mid_price == event.reserve_0 / event.reserve_1
    assert event.invariant == event.reserve_0 * event.reserve_1


def test_uniswap_v2_event_negative_reserves():
    """Test for invalid UniswapV2Event."""
    with pytest.raises(ValueError):
        UniswapV2Event("UNI", "ETH", "USDT", 18, 6, 10, -1000, 2000)


########################################################################################
# Test for class UnsiwapV2Swap
########################################################################################
def test_uniswap_v2_swap_valid():
    """Test for UniswapV2Event class with 500 USDC and 1 ETH."""
    swap_event = UniswapV2Swap(
        "UniswapV2",
        "USDC",
        "WETH",
        6,
        18,
        10,
        1000,
        2000,
        500000000,
        0,
        0,
        1000000000000000000,
    )
    assert swap_event.amount_0 == swap_event.amount_0_in - swap_event.amount_0_out
    assert swap_event.amount_1 == swap_event.amount_1_in - swap_event.amount_1_out
    assert (swap_event.amount_0 * swap_event.amount_1) < 0
    assert swap_event.event_type == DexEventType.SWAP.value


def test_uniswap_v2_swap_invalid_amounts():
    """Test for invalid UniswapV2Swap."""
    with pytest.raises(ValueError):
        UniswapV2Swap(
            "UNI", "ETH", "USDT", 18, 6, 10, 1000, 2000, None, 100, 200, None  # type: ignore[arg-type]
        )


########################################################################################
# Test for class UniswapV2Lp
########################################################################################
def test_uniswap_v2_lp_valid_mint():
    """Test for UniswapV2LP."""
    lp_event = UniswapV2Lp(
        "UniswapV2", "USDC", "WETH", 6, 18, 10, 1000, 2000, 1000, 2000
    )
    assert lp_event.event_type == DexEventType.MINT.value


def test_uniswap_v2_lp_invalid_amounts():
    """Test for UniswapV2Lp where amounts have different signs."""
    with pytest.raises(ValueError):
        UniswapV2Lp("UniswapV2", "USDC", "WETH", 6, 18, 10, 1000, 2000, -1000, 2000)


def test_swap_and_lp_same_event_data_fields():
    """Test to ensure both swap and lp events return the same data fields."""
    # Create a swap event instance
    swap_event = UniswapV2Swap(
        dex_symbol="UNI",
        symbol_0="ETH",
        symbol_1="USDT",
        decimals_0=18,
        decimals_1=6,
        event_index=10,
        reserve_0=1000,
        reserve_1=5000,
        amount_0_in=500,
        amount_0_out=0,
        amount_1_in=0,
        amount_1_out=250,
    )

    # Create an LP event instance
    lp_event = UniswapV2Lp(
        dex_symbol="UNI",
        symbol_0="ETH",
        symbol_1="USDT",
        decimals_0=18,
        decimals_1=6,
        event_index=10,
        reserve_0=1000,
        reserve_1=5000,
        amount_0=500,
        amount_1=250,
    )

    swap_event_data = swap_event.get_event_data()
    lp_event_data = lp_event.get_event_data()

    # Ensure swap_event_data and lp_event_data have the same keys
    assert set(swap_event_data.keys()) == set(lp_event_data.keys())

    # Ensure that certain keys are present in both dictionaries
    expected_keys = {
        "amount_0",
        "amount_0_in",
        "amount_0_out",
        "amount_1",
        "amount_1_in",
        "amount_1_out",
        "decimals_0",
        "decimals_1",
        "event_index",
        "dex_symbol",
        "event_type",
        "invariant",
        "mid_price",
        "reserve_0",
        "reserve_1",
        "symbol_0",
        "symbol_1",
    }
    assert set(swap_event_data.keys()) == expected_keys
    assert set(lp_event_data.keys()) == expected_keys
