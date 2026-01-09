from __future__ import annotations

from unittest.mock import patch

from dexamine.api.parse import parse_positions


def test_parse_positions_wraps_session_generator() -> None:
    expected = [{"events": []}]

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
    expected = [
        {
            "timestamp": 1,
            "block_number": 1,
            "index": 0,
            "event_index": 7,
            "hash": "0xabc",
            "from_address": "0x0000000000000000000000000000000000000001",
            "to_address": "0x0000000000000000000000000000000000000002",
            "value": 0,
            "gas": 1,
            "gasPrice": None,
            "maxPriorityFeePerGas": None,
            "maxFeePerGas": None,
            "event_type": "swap",
            "dex_symbol": "UniswapV2",
            "symbol_0": "A",
            "symbol_1": "B",
            "decimals_0": 18,
            "decimals_1": 18,
            "amount_0": 1.0,
            "amount_1": -1.0,
            "amount_0_in": 1.0,
            "amount_0_out": 0.0,
            "amount_1_in": 0.0,
            "amount_1_out": 1.0,
            "reserve_0": 1.0,
            "reserve_1": 1.0,
            "mid_price": 1.0,
            "invariant": 1.0,
            "to_type": "smart_contract",
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
