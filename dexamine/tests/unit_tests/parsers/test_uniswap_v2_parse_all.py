"""
This file contains unit tests for the Uniswap v2 log-decoding entrypoint,
dexamine/parsers/uniswap_v2_parser.py:parse_all_uniswap_v2_events.

The tests drive the parser end-to-end over synthetic receipt logs with a
pre-populated MetadataResolver, so no node access is required.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from typing import Any

import pytest

# Import modules
from dexamine.parsers import uniswap_v2_parser
from dexamine.shared import constants
from dexamine.tests.helpers import make_metadata_resolver, word, signed_word

POOL = constants.UNISWAP_V2_USDC_WETH_ADDRESS  # USDC/WETH v2 pair
USDC_ADDRESS = constants.USDC_TOKEN_ADDRESS
WETH_ADDRESS = constants.WETH_TOKEN_ADDRESS
OTHER_POOL = "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"  # WETH/USDT v2 pair
TX_HASH = "0x" + "ab" * 32

USDC = 6
WETH = 18


def _resolver() -> Any:
    return make_metadata_resolver(
        v2_pairs={
            POOL: (USDC_ADDRESS, WETH_ADDRESS, "UNI-V2"),
            OTHER_POOL: (USDC_ADDRESS, WETH_ADDRESS, "UNI-V2"),
        },
        erc20={USDC_ADDRESS: ("USDC", USDC), WETH_ADDRESS: ("WETH", WETH)},
    )


def _sync_log(
    address: str = POOL,
    reserve_0: int = 2_000_000_000_000,
    reserve_1: int = 1_000 * 10**18,
) -> dict[str, Any]:
    return {
        "address": address,
        "topics": [constants.UNISWAP_V2_SYNC_EVENT],
        "data": "0x" + word(reserve_0) + word(reserve_1),
        "transactionHash": TX_HASH,
    }


def _swap_log(
    address: str = POOL,
    amount_0_in: int = 1_000_000_000,
    amount_1_in: int = 0,
    amount_0_out: int = 0,
    amount_1_out: int = 5 * 10**17,
) -> dict[str, Any]:
    return {
        "address": address,
        "topics": [constants.UNISWAP_V2_SWAP_EVENT],
        "data": "0x"
        + word(amount_0_in)
        + word(amount_1_in)
        + word(amount_0_out)
        + word(amount_1_out),
        "transactionHash": TX_HASH,
    }


def _lp_log(
    event: str, address: str = POOL, amount_0: int = 1_000_000, amount_1: int = 10**18
) -> dict[str, Any]:
    return {
        "address": address,
        "topics": [event],
        "data": "0x" + word(amount_0) + word(amount_1),
        "transactionHash": TX_HASH,
    }


def _parse(
    logs: list[dict[str, Any]], exchange_pair_address: str = ""
) -> list[dict[str, Any]]:
    return uniswap_v2_parser.parse_all_uniswap_v2_events(
        node_url="http://unused.invalid",
        metadata_resolver=_resolver(),
        logs=logs,
        erc20_abi=[],
        erc20_bytes32_abi=[],
        uniswap_v2_pair_abi=[],
        exchange_pair_address=exchange_pair_address,
    )


########################################################################################
# Swap decoding
########################################################################################
def test_parse_all_v2_events_decodes_a_swap():
    """A sync+swap pair decodes into one swap row with base-unit amounts."""
    logs = [_sync_log(), _swap_log()]
    events = _parse(logs)

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "swap"
    assert event["event_index"] == 1
    assert event["dex_symbol"] == "UNI-V2"
    assert event["symbol_0"] == "USDC"
    assert event["symbol_1"] == "WETH"

    # 1_000_000_000 raw USDC (6 decimals) in, 0.5 WETH (18 decimals) out.
    assert event["amount_0_in"] == pytest.approx(1000.0)
    assert event["amount_1_out"] == pytest.approx(0.5)
    assert event["amount_0"] == pytest.approx(1000.0)
    assert event["amount_1"] == pytest.approx(-0.5)

    # Reserves come from the preceding sync event.
    assert event["reserve_0"] == pytest.approx(2_000_000.0)
    assert event["reserve_1"] == pytest.approx(1000.0)
    assert event["mid_price"] == pytest.approx(2000.0)
    assert event["invariant"] == pytest.approx(2_000_000.0 * 1000.0)


def test_parse_all_v2_events_requires_a_preceding_sync_event():
    """A swap without a preceding sync event from the same pool is skipped."""
    assert _parse([_swap_log()]) == []


def test_parse_all_v2_events_requires_sync_from_the_same_pool():
    """A sync event from a different pool does not satisfy the ordering rule."""
    assert _parse([_sync_log(address=OTHER_POOL), _swap_log()]) == []


########################################################################################
# Mint and burn decoding
########################################################################################
def test_parse_all_v2_events_decodes_a_mint():
    """A sync+mint pair decodes into a mint row with positive amounts."""
    events = _parse([_sync_log(), _lp_log(constants.UNISWAP_V2_MINT_EVENT)])

    assert len(events) == 1
    assert events[0]["event_type"] == "mint"
    assert events[0]["amount_0"] == pytest.approx(1.0)
    assert events[0]["amount_1"] == pytest.approx(1.0)
    # Swap-only columns are padded with None so the schema is stable.
    assert events[0]["amount_0_in"] is None
    assert events[0]["amount_1_out"] is None


def test_parse_all_v2_events_decodes_a_burn_as_negative_amounts():
    """The burn topic flips the sign of both amounts."""
    events = _parse([_sync_log(), _lp_log(constants.UNISWAP_V2_BURN_EVENT)])

    assert len(events) == 1
    assert events[0]["event_type"] == "burn"
    assert events[0]["amount_0"] == pytest.approx(-1.0)
    assert events[0]["amount_1"] == pytest.approx(-1.0)


########################################################################################
# Selection and filtering
########################################################################################
def test_parse_all_v2_events_returns_swaps_and_lps_from_one_receipt():
    """Several Uniswap v2 events in one transaction all come back."""
    logs = [
        _sync_log(),
        _swap_log(),
        _sync_log(),
        _lp_log(constants.UNISWAP_V2_MINT_EVENT),
    ]
    events = _parse(logs)

    assert [event["event_type"] for event in events] == ["swap", "mint"]
    assert [event["event_index"] for event in events] == [1, 3]


def test_parse_all_v2_events_filters_by_pool_address():
    """`exchange_pair_address` keeps only events emitted by that pool."""
    logs = [
        _sync_log(address=OTHER_POOL),
        _swap_log(address=OTHER_POOL),
        _sync_log(address=POOL),
        _swap_log(address=POOL),
    ]

    events = _parse(logs, exchange_pair_address=POOL)
    assert len(events) == 1
    assert events[0]["event_index"] == 3

    events = _parse(logs, exchange_pair_address=OTHER_POOL)
    assert len(events) == 1
    assert events[0]["event_index"] == 1


def test_parse_all_v2_events_ignores_unrelated_logs():
    """Logs that are not Uniswap v2 events produce no rows."""
    erc20_transfer = {
        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "topics": ["0x" + "dd" * 32],
        "data": "0x" + word(1),
        "transactionHash": TX_HASH,
    }
    assert _parse([erc20_transfer]) == []
    assert _parse([]) == []


def test_parse_all_v2_events_handles_large_reserves():
    """Reserve words use the full 32 bytes without truncation."""
    reserve_1 = 2**80 + 12345
    logs = [_sync_log(reserve_1=reserve_1), _swap_log()]
    events = _parse(logs)
    assert events[0]["reserve_1"] == pytest.approx(reserve_1 * 10**-WETH)


def test_signed_word_helper_round_trips():
    """Guard the test helper itself: signed words decode back to their value."""
    from dexamine.shared import general_helpers

    assert general_helpers.parse_signed_int(signed_word(-2)) == -2
    assert general_helpers.parse_signed_int(signed_word(7)) == 7
