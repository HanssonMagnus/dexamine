from __future__ import annotations

from typing import Any

from unittest.mock import patch

import pytest

from dexamine.api.parse import parse_position_raw


def test_parse_position_raw_happy_path() -> None:
    tx_result = {"hash": "0xabc"}
    receipt_result: dict[str, Any] = {"logs": []}
    block_result = {"timestamp": "0x1"}

    def side_effect(*_args, **_kwargs):
        class Response:
            def json(self):
                return payloads.pop(0)

        return Response()

    payloads = [
        {"jsonrpc": "2.0", "id": 1, "result": tx_result},
        {"jsonrpc": "2.0", "id": 2, "result": receipt_result},
        {"jsonrpc": "2.0", "id": 3, "result": block_result},
    ]

    with patch("requests.post", side_effect=side_effect) as mocked_post:
        out = parse_position_raw(
            node_url="http://localhost:8545", block_number=1, tx_index=0
        )

    assert mocked_post.call_count == 3
    assert out["tx"] == tx_result
    assert out["receipt"] == receipt_result
    assert out["block"] == block_result


def test_parse_position_raw_missing_tx_hash_raises() -> None:
    tx_result = {"hash": None}

    payloads = [{"jsonrpc": "2.0", "id": 1, "result": tx_result}]

    def side_effect(*_args, **_kwargs):
        class Response:
            def json(self):
                return payloads.pop(0)

        return Response()

    with patch("requests.post", side_effect=side_effect):
        with pytest.raises(ValueError, match="missing a valid 'hash'"):
            parse_position_raw(
                node_url="http://localhost:8545", block_number=1, tx_index=0
            )
