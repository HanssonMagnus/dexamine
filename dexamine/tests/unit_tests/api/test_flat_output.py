from __future__ import annotations

from dexamine.api.flat_output import iter_flat_rows


def test_iter_flat_rows_uniswap_v2_emits_one_row_per_event_and_none_for_missing_fees() -> (
    None
):
    tx = {
        "hash": "0xabc",
        "from": "0x0000000000000000000000000000000000000001",
        "to": "0x0000000000000000000000000000000000000002",
        "value": "0x0",
        "gas": "0x5208",
        "gasPrice": "0x3b9aca00",
    }
    receipt = {}
    block = {"timestamp": "0x1"}

    events = [
        {
            "event_index": 10,
            "event_type": "swap",
            "dex_symbol": "UniswapV2",
            "symbol_0": "USDC",
            "symbol_1": "WETH",
            "decimals_0": 6,
            "decimals_1": 18,
            "amount_0": 1.0,
            "amount_1": -0.5,
            "amount_0_in": 1.0,
            "amount_0_out": 0.0,
            "amount_1_in": 0.0,
            "amount_1_out": 0.5,
            "reserve_0": 100.0,
            "reserve_1": 50.0,
            "mid_price": 2.0,
            "invariant": 5000.0,
        },
        {
            "event_index": 11,
            "event_type": "mint",
            "dex_symbol": "UniswapV2",
            "symbol_0": "USDC",
            "symbol_1": "WETH",
            "decimals_0": 6,
            "decimals_1": 18,
            "amount_0": 2.0,
            "amount_1": 1.0,
            "amount_0_in": None,
            "amount_0_out": None,
            "amount_1_in": None,
            "amount_1_out": None,
            "reserve_0": 102.0,
            "reserve_1": 51.0,
            "mid_price": 2.0,
            "invariant": 5202.0,
        },
    ]

    rows = list(
        iter_flat_rows(
            protocol="uniswap_v2",
            tx=tx,  # type: ignore[arg-type]
            receipt=receipt,  # type: ignore[arg-type]
            block=block,  # type: ignore[arg-type]
            block_number=100,
            tx_index=5,
            events=events,
        )
    )

    assert len(rows) == 2
    assert rows[0]["index"] == 5
    assert rows[0]["event_index"] == 10
    assert rows[0]["gasPrice"] == int("3b9aca00", 16)
    assert rows[0]["maxPriorityFeePerGas"] is None
    assert rows[0]["maxFeePerGas"] is None

    assert rows[1]["event_index"] == 11
    assert rows[1]["amount_0_in"] is None


def test_iter_flat_rows_uniswap_v3_keeps_optional_fields_as_none() -> None:
    tx = {
        "hash": "0xdef",
        "from": "0x0000000000000000000000000000000000000001",
        "to": "0x0000000000000000000000000000000000000002",
        "value": "0x0",
        "gas": "0x5208",
        "gasPrice": "0x1",
    }
    receipt = {"effectiveGasPrice": "0x2"}
    block = {"timestamp": "0x2"}

    events = [
        {
            "event_index": 7,
            "event_type": "swap",
            "dex_symbol": "UniV3",
            "symbol_0": "USDC",
            "symbol_1": "WETH",
            "decimals_0": 6,
            "decimals_1": 18,
            "sender": "0x0000000000000000000000000000000000000003",
            "recipient": "0x0000000000000000000000000000000000000004",
            "owner": None,
            "amount": None,
            "amount_0": 1.0,
            "amount_1": -0.5,
            "virtual_liquidity": 123,
            "tick": -1,
            "sqrt_price_x96": 456,
            "price": 2000.0,
            "tick_lower": None,
            "tick_upper": None,
            "virtual_reserve_0": 10.0,
            "virtual_reserve_1": 20.0,
        }
    ]

    rows = list(
        iter_flat_rows(
            protocol="uniswap_v3",
            tx=tx,  # type: ignore[arg-type]
            receipt=receipt,  # type: ignore[arg-type]
            block=block,  # type: ignore[arg-type]
            block_number=101,
            tx_index=0,
            events=events,
        )
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["gasPrice"] == 2
    assert row["tick_lower"] is None
    assert row["tick_upper"] is None
    assert row["amount"] is None
