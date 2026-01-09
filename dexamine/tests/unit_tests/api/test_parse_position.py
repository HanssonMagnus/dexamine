from __future__ import annotations

from unittest.mock import patch

from dexamine.api.parse import parse_position


def test_parse_position_uniswap_v2_dispatches_and_returns_events() -> None:
    session_result = {
        "tx": {"hash": "0xabc"},
        "receipt": {"logs": []},
        "block": {"timestamp": "0x1"},
        "events": [{"event_type": "swap"}],
    }

    with patch(
        "dexamine.api.parse.DexamineSession.from_node_url"
    ) as mocked_from_node_url:
        mocked_from_node_url.return_value.parse_position.return_value = session_result
        out = parse_position(
            node_url="http://node",
            block_number=1,
            tx_index=0,
            protocol="uniswap_v2",
            exchange_pair_address=None,
        )

    assert out["tx"] == session_result["tx"]
    assert out["receipt"] == session_result["receipt"]
    assert out["block"] == session_result["block"]
    assert out["events"] == [{"event_type": "swap"}]


def test_parse_position_uniswap_v3_none_becomes_empty_list() -> None:
    session_result = {
        "tx": {"hash": "0xabc"},
        "receipt": {"logs": []},
        "block": {"timestamp": "0x1"},
        "events": [],
    }

    with patch(
        "dexamine.api.parse.DexamineSession.from_node_url"
    ) as mocked_from_node_url:
        mocked_from_node_url.return_value.parse_position.return_value = session_result
        out = parse_position(
            node_url="http://node",
            block_number=1,
            tx_index=0,
            protocol="uniswap_v3",
            exchange_pair_address=None,
        )

    assert out["events"] == session_result["events"]

