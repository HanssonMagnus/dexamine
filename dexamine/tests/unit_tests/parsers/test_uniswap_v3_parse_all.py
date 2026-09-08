"""
This file contains unit tests for the Uniswap v3 log-decoding entrypoint,
dexamine/parsers/uniswap_v3_parser.py:parse_all_v3_events.

The swap/burn cases use synthetic logs; the mint case decodes the real receipt
recorded in dexamine/tests/test_data/node_responses/receipt_data.json (the
transaction that created the USDC/WETH 0.05% pool). No node access is required.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from typing import Any

import pytest

# Import modules
from dexamine.parsers import uniswap_v3_parser
from dexamine.shared import constants, general_helpers
from dexamine.tests.helpers import make_metadata_resolver, signed_word, word

POOL = constants.UNISWAP_V3_USDC_WETH_5BPS_ADDRESS
OTHER_POOL = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"  # USDC/WETH 0.3%
USDC_ADDRESS = constants.USDC_TOKEN_ADDRESS
WETH_ADDRESS = constants.WETH_TOKEN_ADDRESS
TX_HASH = "0x" + "cd" * 32

USDC = 6
WETH = 18

# sqrt(price) as a Q64.96 for a pool priced around 2000 USDC per WETH.
SQRT_PRICE_X96 = 1771595571142957102904975518859264


def _resolver() -> Any:
    return make_metadata_resolver(
        v3_pools={
            POOL: (USDC_ADDRESS, WETH_ADDRESS, "UniV3"),
            OTHER_POOL: (USDC_ADDRESS, WETH_ADDRESS, "UniV3"),
        },
        erc20={USDC_ADDRESS: ("USDC", USDC), WETH_ADDRESS: ("WETH", WETH)},
    )


def _padded_address(address: str) -> str:
    return "0x" + "0" * 24 + address[2:].lower()


def _swap_log(
    address: str = POOL,
    amount_0: int = 1_000_000_000,
    amount_1: int = -5 * 10**17,
    virtual_liquidity: int = 10**20,
    tick: int = -195_000,
) -> dict[str, Any]:
    return {
        "address": address,
        "topics": [
            constants.UNISWAP_V3_SWAP_EVENT,
            _padded_address(constants.UNISWAP_V3_ROUTER_ADDRESS),
            _padded_address(constants.UNISWAP_V3_ROUTER_2_ADDRESS),
        ],
        "data": "0x"
        + signed_word(amount_0)
        + signed_word(amount_1)
        + word(SQRT_PRICE_X96)
        + word(virtual_liquidity)
        + signed_word(tick),
        "transactionHash": TX_HASH,
    }


def _burn_log(
    address: str = POOL,
    amount: int = 10**18,
    amount_0: int = 1_000_000,
    amount_1: int = 10**17,
    tick_lower: int = -196_000,
    tick_upper: int = -194_000,
) -> dict[str, Any]:
    return {
        "address": address,
        "topics": [
            constants.UNISWAP_V3_BURN_EVENT,
            _padded_address(constants.UNISWAP_V3_POSITIONS_NFT_ADDRESS),
            signed_word(tick_lower),
            signed_word(tick_upper),
        ],
        "data": "0x" + word(amount) + word(amount_0) + word(amount_1),
        "transactionHash": TX_HASH,
    }


def _parse(
    logs: list[dict[str, Any]], exchange_pair_address: str = ""
) -> list[dict[str, Any]]:
    return uniswap_v3_parser.parse_all_v3_events(
        node_url="http://unused.invalid",
        metadata_resolver=_resolver(),
        logs=logs,
        erc20_abi=[],
        erc20_bytes32_abi=[],
        uniswap_v3_pair_abi=[],
        exchange_pair_address=exchange_pair_address,
    )


########################################################################################
# Swap decoding
########################################################################################
def test_parse_all_v3_events_decodes_a_swap():
    """A v3 swap log decodes into one row with signed amounts and a base-unit price."""
    events = _parse([_swap_log()])

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "swap"
    assert event["event_index"] == 0
    assert event["dex_symbol"] == "UniV3"
    assert event["symbol_0"] == "USDC"
    assert event["symbol_1"] == "WETH"

    # amount_0 is positive (into the pool), amount_1 negative (out of the pool).
    assert event["amount_0"] == pytest.approx(1000.0)
    assert event["amount_1"] == pytest.approx(-0.5)
    assert event["tick"] == -195_000
    assert event["sqrt_price_x96"] == SQRT_PRICE_X96

    # price = (10**dec1 / 10**dec0) / (sqrtPriceX96 / 2**96)**2
    expected_price = (10**WETH / 10**USDC) / (SQRT_PRICE_X96 / 2**96) ** 2
    assert event["price"] == pytest.approx(expected_price)

    # Mint/burn-only columns are padded with None so the schema stays stable.
    assert event["amount"] is None
    assert event["tick_lower"] is None
    assert event["owner"] is None


def test_parse_all_v3_events_decodes_negative_ticks_as_twos_complement():
    """A negative tick is a two's-complement word, not a huge positive integer."""
    events = _parse([_swap_log(tick=-1)])
    assert events[0]["tick"] == -1


def test_parse_all_v3_events_swap_with_zero_liquidity_has_no_virtual_reserves():
    """
    `liquidity` can be 0 at a tick boundary. The swap is still valid, but virtual
    reserves are not meaningful and must be None rather than 0.
    """
    events = _parse([_swap_log(virtual_liquidity=0)])

    assert len(events) == 1
    assert events[0]["virtual_liquidity"] == 0
    assert events[0]["virtual_reserve_0"] is None
    assert events[0]["virtual_reserve_1"] is None
    # The rest of the row is unaffected.
    assert events[0]["amount_0"] == pytest.approx(1000.0)


def test_parse_all_v3_events_swap_with_liquidity_has_virtual_reserves():
    """With non-zero liquidity both virtual reserves are populated."""
    events = _parse([_swap_log()])
    assert events[0]["virtual_reserve_0"] is not None
    assert events[0]["virtual_reserve_1"] is not None
    assert events[0]["virtual_reserve_0"] > 0
    assert events[0]["virtual_reserve_1"] > 0


########################################################################################
# Mint decoding (real recorded receipt)
########################################################################################
def test_parse_all_v3_events_decodes_a_mint_from_a_recorded_receipt():
    """Decode the v3 mint in the recorded USDC/WETH 0.05% pool-creation receipt."""
    receipt = general_helpers.get_json_test_data("node_responses/receipt_data.json")
    logs = receipt["result"]["logs"]

    events = _parse(logs)

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "mint"
    assert event["event_index"] == 5  # the Mint log's index within the receipt
    assert event["symbol_0"] == "USDC"
    assert event["symbol_1"] == "WETH"
    assert event["amount"] > 0
    assert event["amount_0"] >= 0
    assert event["amount_1"] >= 0
    assert event["tick_lower"] < event["tick_upper"]
    assert event["owner"].startswith("0x")
    # Swap-only columns are padded with None.
    assert event["price"] is None
    assert event["sqrt_price_x96"] is None


########################################################################################
# Burn decoding
########################################################################################
def test_parse_all_v3_events_decodes_a_burn():
    """A v3 burn log decodes into a burn row with negative token amounts."""
    events = _parse([_burn_log()])

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "burn"
    assert event["tick_lower"] == -196_000
    assert event["tick_upper"] == -194_000
    assert event["amount_0"] == pytest.approx(-1.0)
    assert event["amount_1"] == pytest.approx(-0.1)


########################################################################################
# Selection and filtering
########################################################################################
def test_parse_all_v3_events_returns_every_matching_event():
    """Several v3 events in one transaction all come back, in log order."""
    events = _parse([_swap_log(), _burn_log(), _swap_log()])
    assert [event["event_type"] for event in events] == ["swap", "swap", "burn"]
    assert sorted(event["event_index"] for event in events) == [0, 1, 2]


def test_parse_all_v3_events_filters_by_pool_address():
    """`exchange_pair_address` keeps only events emitted by that pool."""
    logs = [_swap_log(address=OTHER_POOL), _swap_log(address=POOL)]

    events = _parse(logs, exchange_pair_address=POOL)
    assert len(events) == 1
    assert events[0]["event_index"] == 1

    events = _parse(logs, exchange_pair_address=OTHER_POOL)
    assert len(events) == 1
    assert events[0]["event_index"] == 0


def test_parse_all_v3_events_ignores_unrelated_logs():
    """Logs that are not Uniswap v3 events produce no rows."""
    erc20_transfer = {
        "address": USDC_ADDRESS,
        "topics": ["0x" + "dd" * 32],
        "data": "0x" + word(1),
        "transactionHash": TX_HASH,
    }
    assert _parse([erc20_transfer]) == []
    assert _parse([]) == []
