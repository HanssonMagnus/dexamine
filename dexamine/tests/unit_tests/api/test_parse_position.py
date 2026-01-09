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


def test_parse_position_flat_returns_rows() -> None:
    expected_rows = [
        {
            "block_timestamp": 1,
            "block_number": 1,
            "block_gas": 0,
            "block_txes": 0,
            "tx_index": 0,
            "log_index": 7,
            "tx_hash": "0xabc",
            "tx_from": "0x0000000000000000000000000000000000000001",
            "tx_to": "0x0000000000000000000000000000000000000002",
            "tx_value": 0,
            "tx_gas": 1,
            "tx_gas_price": None,
            "tx_max_priority_fee_per_gas": None,
            "tx_max_fee_per_gas": None,
            "tx_to_type": "smart_contract",
            "event_type": "swap",
            "event_dex_symbol": "UniswapV2",
            "event_symbol_0": "A",
            "event_symbol_1": "B",
            "event_decimals_0": 18,
            "event_decimals_1": 18,
            "event_amount_0": 1.0,
            "event_amount_1": -1.0,
            "event_amount_0_in": 1.0,
            "event_amount_0_out": 0.0,
            "event_amount_1_in": 0.0,
            "event_amount_1_out": 1.0,
            "event_reserve_0": 1.0,
            "event_reserve_1": 1.0,
            "event_mid_price": 1.0,
            "event_invariant": 1.0,
        }
    ]

    with patch(
        "dexamine.api.parse.DexamineSession.from_node_url"
    ) as mocked_from_node_url:
        mocked_from_node_url.return_value.parse_position.return_value = expected_rows
        out = parse_position(
            node_url="http://node",
            block_number=1,
            tx_index=0,
            protocol="uniswap_v2",
            exchange_pair_address=None,
            output_format="flat",
        )

    assert out == expected_rows
