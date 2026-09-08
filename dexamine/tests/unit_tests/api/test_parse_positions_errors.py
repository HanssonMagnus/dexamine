"""
This file contains unit tests for error handling in the batched parsing path,
dexamine/api/session.py:DexamineSession.parse_positions.

A JSON-RPC node may legitimately answer a batched request with `result: null`
(for example for a transaction it does not have). Those cases must raise the same
informative errors as the single-call path.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

from __future__ import annotations

from typing import Any

import pytest

from dexamine.api.session import DexamineSession
from dexamine.rpc.json_rpc_client import (
    JsonRpcResponseFormatError,
    JsonRpcResultNotFoundError,
)

BLOCK = 12_376_729
TX_INDEX = 3
TX_HASH = "0x" + "ef" * 32


class _StubRpc:
    """A JsonRpcClient stand-in that replays canned batch responses."""

    def __init__(self, responses: list[dict[int, Any]]) -> None:
        self._responses = responses
        self.calls = 0

    def batch_call(self, calls: list[tuple[str, list[Any], int]]) -> dict[int, Any]:
        response = self._responses[self.calls]
        self.calls += 1
        return response


def _session(responses: list[dict[int, Any]]) -> DexamineSession:
    session = DexamineSession.from_node_url("http://unused.invalid")
    return DexamineSession(
        node_url=session.node_url,
        rpc=_StubRpc(responses),  # type: ignore[arg-type]
        erc20_abi=session.erc20_abi,
        erc20_bytes32_abi=session.erc20_bytes32_abi,
        uniswap_v2_pair_abi=session.uniswap_v2_pair_abi,
        uniswap_v3_pair_abi=session.uniswap_v3_pair_abi,
        metadata=session.metadata,
    )


def _drain(session: DexamineSession) -> None:
    list(
        session.parse_positions(
            positions=[(BLOCK, TX_INDEX)],
            protocol="uniswap_v3",
            exchange_pair_address=None,
            batch_size=10,
        )
    )


def test_parse_positions_raises_when_a_transaction_is_missing():
    """A null transaction result names the position that could not be fetched."""
    session = _session([{1: None}])

    with pytest.raises(JsonRpcResultNotFoundError) as excinfo:
        _drain(session)

    assert f"block_number={BLOCK}" in str(excinfo.value)
    assert f"tx_index={TX_INDEX}" in str(excinfo.value)


def test_parse_positions_raises_when_a_receipt_is_missing():
    """A null receipt result names the position and the transaction hash."""
    session = _session(
        [
            {1: {"hash": TX_HASH}},
            {1: None},
            {1: {"timestamp": "0x1", "transactions": []}},
        ]
    )

    with pytest.raises(JsonRpcResultNotFoundError) as excinfo:
        _drain(session)

    assert f"block_number={BLOCK}" in str(excinfo.value)
    assert TX_HASH in str(excinfo.value)


def test_parse_positions_raises_when_a_block_is_missing():
    """A null block result names the block that could not be fetched."""
    session = _session(
        [{1: {"hash": TX_HASH}}, {1: {"logs": []}}, {1: None}],
    )

    with pytest.raises(JsonRpcResultNotFoundError) as excinfo:
        _drain(session)

    assert f"block_number={BLOCK}" in str(excinfo.value)


def test_parse_positions_raises_on_a_malformed_result():
    """A non-object result is a format error, not a lookup error."""
    session = _session([{1: "not-an-object"}])

    with pytest.raises(JsonRpcResponseFormatError):
        _drain(session)


def test_parse_positions_raises_when_a_transaction_has_no_hash():
    """A transaction object without a usable hash names the position."""
    session = _session([{1: {"blockNumber": "0xbcd"}}])

    with pytest.raises(ValueError) as excinfo:
        _drain(session)

    assert str((BLOCK, TX_INDEX)) in str(excinfo.value)
