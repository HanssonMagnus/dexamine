from __future__ import annotations

from unittest.mock import patch

from dexamine.api.parse import parse_positions


def test_parse_positions_wraps_session_generator() -> None:
    expected = [{"events": []}]

    with patch("dexamine.api.parse.DexamineSession.from_node_url") as mocked_from_node_url:
        mocked_from_node_url.return_value.parse_positions.return_value = iter(expected)
        out = parse_positions(
            node_url="http://node",
            positions=[(1, 0)],
            protocol="uniswap_v2",
            exchange_pair_address=None,
            batch_size=10,
        )

    assert out == expected

