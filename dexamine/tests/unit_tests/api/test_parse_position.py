from __future__ import annotations

from unittest.mock import patch

from dexamine.api.parse import parse_position


def test_parse_position_uniswap_v2_dispatches_and_returns_events() -> None:
    raw = {"tx": {"hash": "0xabc"}, "receipt": {"logs": []}, "block": {"timestamp": "0x1"}}

    with patch("dexamine.api.parse.parse_position_raw", return_value=raw):
        with patch("dexamine.shared.general_helpers.get_json_abi", return_value={"abi": "x"}):
            with patch(
                "dexamine.parsers.uniswap_v2_parser.parse_all_uniswap_v2_events",
                return_value=[{"event_type": "swap"}],
            ) as mocked_parse:
                out = parse_position(
                    node_url="http://node",
                    block_number=1,
                    tx_index=0,
                    protocol="uniswap_v2",
                    exchange_pair_address=None,
                )

    mocked_parse.assert_called_once()
    assert out["tx"] == raw["tx"]
    assert out["receipt"] == raw["receipt"]
    assert out["block"] == raw["block"]
    assert out["events"] == [{"event_type": "swap"}]


def test_parse_position_uniswap_v3_none_becomes_empty_list() -> None:
    raw = {"tx": {"hash": "0xabc"}, "receipt": {"logs": []}, "block": {"timestamp": "0x1"}}

    with patch("dexamine.api.parse.parse_position_raw", return_value=raw):
        with patch("dexamine.shared.general_helpers.get_json_abi", return_value={"abi": "x"}):
            with patch(
                "dexamine.parsers.uniswap_v3_parser.parse_all_v3_events", return_value=None
            ):
                out = parse_position(
                    node_url="http://node",
                    block_number=1,
                    tx_index=0,
                    protocol="uniswap_v3",
                    exchange_pair_address=None,
                )

    assert out["events"] == []

