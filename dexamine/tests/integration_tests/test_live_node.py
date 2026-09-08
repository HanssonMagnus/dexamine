"""
Opt-in integration tests that talk to a real Ethereum JSON-RPC endpoint.

These tests are skipped unless the `DEXAMINE_NODE_URL` environment variable is set,
so the default `pytest dexamine/` run stays offline and deterministic:

    DEXAMINE_NODE_URL=https://ethereum-rpc.publicnode.com \
        python -m pytest dexamine/ -m integration

dexamine reads token and pool metadata at the *latest* block, so an archive node
(historical state) is not required. What is required is a node that still serves the
blocks and receipts you want to parse. The positions below are from 2020 and 2021, so a
pruned endpoint cannot serve them; in that case these tests skip with an explanatory
message rather than failing.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

from __future__ import annotations

import os
from typing import Any, Callable, TypeVar

import pytest

from dexamine import DexamineSession, parse_position
from dexamine.api.flat_output import FLAT_UNISWAP_V3_COLUMNS
from dexamine.rpc.json_rpc_client import JsonRpcError, JsonRpcResultNotFoundError
from dexamine.shared import constants

NODE_URL = os.environ.get("DEXAMINE_NODE_URL")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not NODE_URL,
        reason="set DEXAMINE_NODE_URL to run the live-node integration tests",
    ),
]

# The transaction that created the Uniswap v3 USDC/WETH 0.05% pool and minted the first
# position. Block 12,376,729 on Ethereum mainnet, transaction index 59.
V3_MINT_BLOCK = 12_376_729
V3_MINT_TX_INDEX = 59

# A Uniswap v2 swap routed through the v2 router, used by the README quickstart.
V2_SWAP_BLOCK = 10_008_566
V2_SWAP_TX_INDEX = 1

T = TypeVar("T")


# Substrings that mark an endpoint limitation rather than a dexamine defect.
_ENDPOINT_LIMITS = ("pruned", "not found", "rate limit", "unauthorized", "too many")


def _needing_history(call: Callable[[], T]) -> T:
    """
    Run `call`, skipping the test when the endpoint cannot serve the request.

    Public endpoints are frequently pruned or rate limited. Those are properties of
    the endpoint, not of dexamine, so they skip with an explanatory message instead
    of failing the suite.
    """
    try:
        return call()
    except (JsonRpcError, JsonRpcResultNotFoundError) as exc:
        message = str(exc)
        if any(limit in message.lower() for limit in _ENDPOINT_LIMITS):
            pytest.skip(
                f"{NODE_URL} could not serve the request: {message}. "
                "Use an endpoint that retains the required history and is not rate "
                "limited (a full non-pruned node, or an archive node)."
            )
        raise


def _number(value: Any) -> float:
    """Assert that a parsed field is numeric and return it as a float."""
    assert isinstance(value, (int, float)) and not isinstance(value, bool)
    return float(value)


def test_parse_position_raw_fetches_tx_receipt_and_block():
    """The raw fetch returns the three JSON-RPC payloads for a known position."""
    session = DexamineSession.from_node_url(str(NODE_URL))
    raw = _needing_history(
        lambda: session.parse_position_raw(
            block_number=V3_MINT_BLOCK, tx_index=V3_MINT_TX_INDEX
        )
    )

    assert set(raw) == {"tx", "receipt", "block"}
    assert int(str(raw["tx"]["transactionIndex"]), 16) == V3_MINT_TX_INDEX
    assert int(str(raw["block"]["number"]), 16) == V3_MINT_BLOCK
    assert raw["receipt"]["transactionHash"] == raw["tx"]["hash"]


def test_parse_position_decodes_the_v3_mint():
    """Parsing the known pool-creation transaction yields exactly one mint event."""
    result = _needing_history(
        lambda: parse_position(
            node_url=str(NODE_URL),
            block_number=V3_MINT_BLOCK,
            tx_index=V3_MINT_TX_INDEX,
            protocol="uniswap_v3",
            exchange_pair_address=None,
        )
    )

    events = result["events"]
    assert len(events) == 1
    assert events[0]["event_type"] == "mint"
    assert events[0]["symbol_0"] == "USDC"
    assert events[0]["symbol_1"] == "WETH"
    assert events[0]["dex_symbol"] == "UniV3"


def test_flat_output_matches_the_documented_schema():
    """Flat rows carry exactly the documented Uniswap v3 columns."""
    rows = _needing_history(
        lambda: parse_position(
            node_url=str(NODE_URL),
            block_number=V3_MINT_BLOCK,
            tx_index=V3_MINT_TX_INDEX,
            protocol="uniswap_v3",
            exchange_pair_address=None,
            output_format="flat",
        )
    )

    assert len(rows) == 1
    assert tuple(rows[0]) == FLAT_UNISWAP_V3_COLUMNS
    assert rows[0]["block_number"] == V3_MINT_BLOCK
    assert rows[0]["tx_index"] == V3_MINT_TX_INDEX
    # This transaction was sent to the Uniswap v3 positions NFT manager, one of the
    # canonical Uniswap deployments in `constants.uniswap_address_list`.
    assert rows[0]["tx_to_type"] == "uniswap_router"


def test_pool_address_filter_excludes_other_pools():
    """Filtering on an unrelated pool returns no events."""
    result = _needing_history(
        lambda: parse_position(
            node_url=str(NODE_URL),
            block_number=V3_MINT_BLOCK,
            tx_index=V3_MINT_TX_INDEX,
            protocol="uniswap_v3",
            exchange_pair_address=constants.UNISWAP_V2_USDC_WETH_ADDRESS,
        )
    )
    assert result["events"] == []


def test_parse_positions_batches_several_positions():
    """The batched generator returns one result per requested position."""
    session = DexamineSession.from_node_url(str(NODE_URL))
    positions = [(V3_MINT_BLOCK, V3_MINT_TX_INDEX), (V3_MINT_BLOCK, 0)]

    results = _needing_history(
        lambda: list(
            session.parse_positions(
                positions=positions,
                protocol="uniswap_v3",
                exchange_pair_address=None,
                batch_size=10,
            )
        )
    )

    assert len(results) == len(positions)
    assert all(
        set(result) == {"tx", "receipt", "block", "events"} for result in results
    )


def test_parse_position_decodes_a_uniswap_v2_swap():
    """The Uniswap v2 example used in the README and docs decodes to one swap."""
    result = _needing_history(
        lambda: parse_position(
            node_url=str(NODE_URL),
            block_number=V2_SWAP_BLOCK,
            tx_index=V2_SWAP_TX_INDEX,
            protocol="uniswap_v2",
            exchange_pair_address=None,
        )
    )

    events = result["events"]
    assert len(events) == 1
    assert events[0]["event_type"] == "swap"
    # A v2 swap always reports both reserves and the resulting mid price.
    assert _number(events[0]["reserve_0"]) > 0
    assert _number(events[0]["reserve_1"]) > 0
    assert _number(events[0]["mid_price"]) > 0
