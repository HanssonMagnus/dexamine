from __future__ import annotations

from typing import Dict, List
from unittest.mock import patch

from dexamine.api.parse import parse_positions


def test_parse_positions_wraps_session_generator() -> None:
    expected: List[Dict[str, object]] = [{"events": []}]

    with patch(
        "dexamine.api.parse.DexamineSession.from_node_url"
    ) as mocked_from_node_url:
        mocked_from_node_url.return_value.parse_positions.return_value = iter(expected)
        out = parse_positions(
            node_url="http://node",
            positions=[(1, 0)],
            protocol="uniswap_v2",
            exchange_pair_address=None,
            batch_size=10,
        )

    assert out == expected


def test_parse_positions_flat_wraps_session_generator() -> None:
    expected: List[Dict[str, object]] = [
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
        mocked_from_node_url.return_value.parse_positions.return_value = iter(expected)
        out = parse_positions(
            node_url="http://node",
            positions=[(1, 0)],
            protocol="uniswap_v2",
            exchange_pair_address=None,
            batch_size=10,
            output_format="flat",
        )

    assert out == expected
