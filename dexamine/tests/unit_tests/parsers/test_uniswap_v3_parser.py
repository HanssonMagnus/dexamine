"""
This file contains unit tests for the classes and functions in
dexamine/parsers/uniswap_v3_parser.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import pytest

# Import modules
from dexamine.shared.general_classes import DexEventType
from dexamine.parsers.uniswap_v3_parser import (
    UniswapV3Swap,
    UniswapV3Mint,
    UniswapV3Burn,
)
from dexamine.parsers import uniswap_v3_parser


########################################################################################
# Define fixtures for the UniswapV3Swap, UniswapV3Mint, and UniswapV3Burn instances
########################################################################################
@pytest.fixture
def swap_event():
    """Fixture for Uniswap V3 swap event."""
    return UniswapV3Swap(
        dex_symbol="UniV3",
        symbol_0="USDC",
        symbol_1="WETH",
        decimals_0=6,
        decimals_1=18,
        event_index=10,
        sender="0xSender",
        recipient="0xRecipient",
        amount_0=2187793161,
        amount_1=-741458298565724583,
        sqrt_price_x96=1458905354048256518860025704567282,
        virtual_liquidity=6718764696431944105,
        tick=196427,
    )


@pytest.fixture
def mint_event():
    """Fixture for Uniswap V3 mint event. Data from transaction:
    0xef93747acabe06ab11f663321f0de466bf9ae35888baf7bd9f6baad12e90037e
    """
    return UniswapV3Mint(
        dex_symbol="UniV3",
        symbol_0="USDC",
        symbol_1="WETH",
        decimals_0=6,
        decimals_1=18,
        event_index=10,
        sender="0xSender",
        owner="0xOwner",
        tick_lower=186730,
        tick_upper=195460,
        amount=447994594415865,
        amount_0=598469729,
        amount_1=2599999995846641821,
    )


@pytest.fixture
def burn_event():
    """Fixture for Uniswap V3 burn event. Data from transaction:
    0x0071c57b5c72215b9eb61237306078b0d66bc4b7477f2ad6367511c14caf13bd
    """
    return UniswapV3Burn(
        dex_symbol="UniV3",
        symbol_0="USDC",
        symbol_1="WETH",
        decimals_0=6,
        decimals_1=18,
        event_index=10,
        owner="0xOwner",
        tick_lower=194750,
        tick_upper=194790,
        amount=1499570648517615,
        amount_0=-0,
        amount_1=-50832403254742608,
    )


########################################################################################
# Test for class UniswapV3Swap
########################################################################################
def test_swap_event(swap_event):
    """Test values of Uniswap v3 swap event."""
    assert swap_event.dex_symbol == "UniV3"
    assert swap_event.symbol_0 == "USDC"
    assert swap_event.symbol_1 == "WETH"
    assert swap_event.decimals_0 == 6
    assert swap_event.decimals_1 == 18
    assert swap_event.sender == "0xSender"
    assert swap_event.event_index == 10
    assert swap_event.recipient == "0xRecipient"
    assert swap_event.sqrt_price_x96 == 1458905354048256518860025704567282
    assert swap_event.virtual_liquidity == 6718764696431944105
    assert swap_event.tick == 196427
    assert swap_event.amount_0 == 2187.793161
    assert swap_event.amount_1 == -0.7414582985657246
    assert swap_event.price == 2949.2047945032405
    assert swap_event.virtual_reserve_0 == 364873142.58386385
    assert swap_event.virtual_reserve_1 == 123719.16092904717
    assert (
        swap_event.virtual_reserve_0 / swap_event.virtual_reserve_1 == 2949.20479450324
    )
    assert swap_event.event_type == DexEventType.SWAP.value
    # LP values
    assert swap_event.get_event_data()["amount"] == None
    assert swap_event.get_event_data()["owner"] == None
    assert swap_event.get_event_data()["tick_lower"] == None
    assert swap_event.get_event_data()["tick_upper"] == None


########################################################################################
# Test for class UniswapV3Mint
########################################################################################
def test_mint_event(mint_event):
    """Test values of Unimint v3 mint event."""
    assert mint_event.dex_symbol == "UniV3"
    assert mint_event.symbol_0 == "USDC"
    assert mint_event.symbol_1 == "WETH"
    assert mint_event.decimals_0 == 6
    assert mint_event.decimals_1 == 18
    assert mint_event.event_index == 10
    assert mint_event.sender == "0xSender"
    assert mint_event.owner == "0xOwner"
    assert mint_event.tick_lower == 186730
    assert mint_event.tick_upper == 195460
    assert mint_event.amount == 447994594415865
    assert mint_event.amount_0 == 598.469729
    assert mint_event.amount_1 == 2.59999999584664182
    assert mint_event.event_type == DexEventType.MINT.value
    # Swap values
    assert mint_event.get_event_data()["recipient"] == None
    assert mint_event.get_event_data()["sqrt_price_x96"] == None
    assert mint_event.get_event_data()["virtual_liquidity"] == None
    assert mint_event.get_event_data()["tick"] == None
    assert mint_event.get_event_data()["price"] == None
    assert mint_event.get_event_data()["virtual_reserve_0"] == None
    assert mint_event.get_event_data()["virtual_reserve_1"] == None


def test_uniswap_v3_mint_invalid_amounts():
    """Test for UniswapV2Mint where amounts are not positive."""
    with pytest.raises(ValueError):
        UniswapV3Mint(
            "UniV3",
            "USDC",
            "WETH",
            6,
            18,
            10,
            "0xSender",
            "0xOwner",
            186730,
            195460,
            447994594415865,
            598469729,
            -2599999995846641821,
        )


########################################################################################
# Test for class UniswapV3Burn
########################################################################################
def test_burn_event(burn_event):
    """Test values of Uniburn v3 burn event."""
    assert burn_event.dex_symbol == "UniV3"
    assert burn_event.symbol_0 == "USDC"
    assert burn_event.symbol_1 == "WETH"
    assert burn_event.decimals_0 == 6
    assert burn_event.decimals_1 == 18
    assert burn_event.event_index == 10
    assert burn_event.owner == "0xOwner"
    assert burn_event.tick_lower == 194750
    assert burn_event.tick_upper == 194790
    assert burn_event.amount == 1499570648517615
    assert burn_event.amount_0 == 0
    assert burn_event.amount_1 == -0.050832403254742614
    assert burn_event.event_type == DexEventType.BURN.value
    # Swap values
    assert burn_event.get_event_data()["sender"] == None
    assert burn_event.get_event_data()["recipient"] == None
    assert burn_event.get_event_data()["sqrt_price_x96"] == None
    assert burn_event.get_event_data()["virtual_liquidity"] == None
    assert burn_event.get_event_data()["tick"] == None
    assert burn_event.get_event_data()["price"] == None
    assert burn_event.get_event_data()["virtual_reserve_0"] == None
    assert burn_event.get_event_data()["virtual_reserve_1"] == None


def test_uniswap_v3_burn_invalid_amounts():
    """Test for UniswapV2Burn where amounts are not positive."""
    with pytest.raises(ValueError):
        UniswapV3Burn(
            "UniV3",
            "USDC",
            "WETH",
            6,
            18,
            10,
            "0xOwner",
            186730,
            195460,
            447994594415865,
            598469729,
            -2599999995846641821,
        )
