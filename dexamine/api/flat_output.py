"""
Helpers for converting nested parse results into flat, CSV-friendly rows.

Flat output is designed to be streaming-friendly for very large workloads.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Literal, TypedDict

from dexamine.rpc.json_rpc_client import JsonObject
from dexamine.shared.general_helpers import parse_to_type

Protocol = Literal["uniswap_v2", "uniswap_v3"]


class _BaseFlatRow(TypedDict):
    timestamp: int
    block_number: int
    index: int
    event_index: int
    hash: str
    from_address: str
    to_address: str | None
    value: int
    gas: int
    gasPrice: int | None
    maxPriorityFeePerGas: int | None
    maxFeePerGas: int | None
    event_type: str
    dex_symbol: str
    symbol_0: str
    symbol_1: str
    decimals_0: int
    decimals_1: int
    to_type: str


class FlatUniswapV2Row(_BaseFlatRow):
    amount_0: float
    amount_1: float
    amount_0_in: float | None
    amount_0_out: float | None
    amount_1_in: float | None
    amount_1_out: float | None
    reserve_0: float
    reserve_1: float
    mid_price: float
    invariant: float


class FlatUniswapV3Row(_BaseFlatRow):
    sender: str | None
    recipient: str | None
    owner: str | None
    amount: float | None
    amount_0: float
    amount_1: float
    virtual_liquidity: float | None
    tick: int | None
    sqrt_price_x96: float | None
    price: float | None
    tick_lower: int | None
    tick_upper: int | None
    virtual_reserve_0: float | None
    virtual_reserve_1: float | None


FlatRow = FlatUniswapV2Row | FlatUniswapV3Row


FLAT_UNISWAP_V2_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "block_number",
    "index",
    "event_index",
    "hash",
    "from_address",
    "to_address",
    "value",
    "gas",
    "gasPrice",
    "maxPriorityFeePerGas",
    "maxFeePerGas",
    "event_type",
    "dex_symbol",
    "symbol_0",
    "symbol_1",
    "decimals_0",
    "decimals_1",
    "amount_0",
    "amount_1",
    "amount_0_in",
    "amount_0_out",
    "amount_1_in",
    "amount_1_out",
    "reserve_0",
    "reserve_1",
    "mid_price",
    "invariant",
    "to_type",
)


FLAT_UNISWAP_V3_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "block_number",
    "index",
    "event_index",
    "hash",
    "from_address",
    "to_address",
    "value",
    "gas",
    "gasPrice",
    "maxPriorityFeePerGas",
    "maxFeePerGas",
    "event_type",
    "dex_symbol",
    "symbol_0",
    "symbol_1",
    "decimals_0",
    "decimals_1",
    "sender",
    "recipient",
    "owner",
    "amount",
    "amount_0",
    "amount_1",
    "virtual_liquidity",
    "tick",
    "sqrt_price_x96",
    "price",
    "tick_lower",
    "tick_upper",
    "virtual_reserve_0",
    "virtual_reserve_1",
    "to_type",
)


def _parse_hex_int(*, value: object, field_name: str) -> int:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty hex string")
    return int(value, 16)


def _parse_hex_int_optional(*, value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        return None
    return int(value, 16)


def _parse_timestamp(*, block: JsonObject) -> int:
    return _parse_hex_int(value=block.get("timestamp"), field_name="block.timestamp")


def _tx_hash(*, tx: JsonObject) -> str:
    hash_value = tx.get("hash")
    if not isinstance(hash_value, str) or not hash_value:
        raise ValueError("Transaction is missing a valid 'hash' field")
    return hash_value


def _tx_from(*, tx: JsonObject) -> str:
    from_value = tx.get("from")
    if not isinstance(from_value, str) or not from_value:
        raise ValueError("Transaction is missing a valid 'from' field")
    return from_value


def _tx_to(*, tx: JsonObject) -> str | None:
    to_value = tx.get("to")
    if to_value is None:
        return None
    if not isinstance(to_value, str) or not to_value:
        raise ValueError("Transaction has invalid 'to' field")
    return to_value


def _tx_value(*, tx: JsonObject) -> int:
    return _parse_hex_int(value=tx.get("value"), field_name="tx.value")


def _tx_gas(*, tx: JsonObject) -> int:
    return _parse_hex_int(value=tx.get("gas"), field_name="tx.gas")


def _tx_gas_price(*, tx: JsonObject, receipt: JsonObject) -> int | None:
    effective = receipt.get("effectiveGasPrice")
    if effective is not None:
        return _parse_hex_int_optional(value=effective)
    return _parse_hex_int_optional(value=tx.get("gasPrice"))


def _tx_max_priority_fee(*, tx: JsonObject) -> int | None:
    return _parse_hex_int_optional(value=tx.get("maxPriorityFeePerGas"))


def _tx_max_fee(*, tx: JsonObject) -> int | None:
    return _parse_hex_int_optional(value=tx.get("maxFeePerGas"))


def _base_row(
    *,
    tx: JsonObject,
    receipt: JsonObject,
    block: JsonObject,
    block_number: int,
    tx_index: int,
) -> dict[str, object]:
    to_address = _tx_to(tx=tx)
    return {
        "timestamp": _parse_timestamp(block=block),
        "block_number": block_number,
        "index": tx_index,
        "hash": _tx_hash(tx=tx),
        "from_address": _tx_from(tx=tx),
        "to_address": to_address,
        "value": _tx_value(tx=tx),
        "gas": _tx_gas(tx=tx),
        "gasPrice": _tx_gas_price(tx=tx, receipt=receipt),
        "maxPriorityFeePerGas": _tx_max_priority_fee(tx=tx),
        "maxFeePerGas": _tx_max_fee(tx=tx),
        "to_type": parse_to_type(to_address),
    }


def iter_flat_rows(
    *,
    protocol: Protocol,
    tx: JsonObject,
    receipt: JsonObject,
    block: JsonObject,
    block_number: int,
    tx_index: int,
    events: Iterable[dict[str, float | int | str | None]],
) -> Iterator[FlatRow]:
    """
    Yield one flat row per event.

    Notes:
    - This is intentionally a generator for scalability.
    - Missing numeric fields must be None (not 0).
    """
    base = _base_row(
        tx=tx,
        receipt=receipt,
        block=block,
        block_number=block_number,
        tx_index=tx_index,
    )

    if protocol == "uniswap_v2":
        for event in events:
            event_index_value = event.get("event_index")
            if not isinstance(event_index_value, int):
                raise TypeError("Uniswap v2 event is missing 'event_index' as int")

            row: FlatUniswapV2Row = {
                **base,
                "event_index": event_index_value,
                "event_type": _required_str(event=event, field="event_type"),
                "dex_symbol": _required_str(event=event, field="dex_symbol"),
                "symbol_0": _required_str(event=event, field="symbol_0"),
                "symbol_1": _required_str(event=event, field="symbol_1"),
                "decimals_0": _required_int(event=event, field="decimals_0"),
                "decimals_1": _required_int(event=event, field="decimals_1"),
                "amount_0": _required_float(event=event, field="amount_0"),
                "amount_1": _required_float(event=event, field="amount_1"),
                "amount_0_in": _optional_float(event=event, field="amount_0_in"),
                "amount_0_out": _optional_float(event=event, field="amount_0_out"),
                "amount_1_in": _optional_float(event=event, field="amount_1_in"),
                "amount_1_out": _optional_float(event=event, field="amount_1_out"),
                "reserve_0": _required_float(event=event, field="reserve_0"),
                "reserve_1": _required_float(event=event, field="reserve_1"),
                "mid_price": _required_float(event=event, field="mid_price"),
                "invariant": _required_float(event=event, field="invariant"),
            }
            yield row
        return

    if protocol == "uniswap_v3":
        for event in events:
            event_index_value = event.get("event_index")
            if not isinstance(event_index_value, int):
                raise TypeError("Uniswap v3 event is missing 'event_index' as int")

            row: FlatUniswapV3Row = {
                **base,
                "event_index": event_index_value,
                "event_type": _required_str(event=event, field="event_type"),
                "dex_symbol": _required_str(event=event, field="dex_symbol"),
                "symbol_0": _required_str(event=event, field="symbol_0"),
                "symbol_1": _required_str(event=event, field="symbol_1"),
                "decimals_0": _required_int(event=event, field="decimals_0"),
                "decimals_1": _required_int(event=event, field="decimals_1"),
                "sender": _optional_str(event=event, field="sender"),
                "recipient": _optional_str(event=event, field="recipient"),
                "owner": _optional_str(event=event, field="owner"),
                "amount": _optional_float(event=event, field="amount"),
                "amount_0": _required_float(event=event, field="amount_0"),
                "amount_1": _required_float(event=event, field="amount_1"),
                "virtual_liquidity": _optional_float(
                    event=event, field="virtual_liquidity"
                ),
                "tick": _optional_int(event=event, field="tick"),
                "sqrt_price_x96": _optional_float(event=event, field="sqrt_price_x96"),
                "price": _optional_float(event=event, field="price"),
                "tick_lower": _optional_int(event=event, field="tick_lower"),
                "tick_upper": _optional_int(event=event, field="tick_upper"),
                "virtual_reserve_0": _optional_float(
                    event=event, field="virtual_reserve_0"
                ),
                "virtual_reserve_1": _optional_float(
                    event=event, field="virtual_reserve_1"
                ),
            }
            yield row
        return

    raise ValueError(f"Unsupported protocol: {protocol}")


def _required_str(*, event: dict[str, object], field: str) -> str:
    value = event.get(field)
    if not isinstance(value, str) or not value:
        raise TypeError(f"Event field '{field}' must be a non-empty str")
    return value


def _optional_str(*, event: dict[str, object], field: str) -> str | None:
    value = event.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise TypeError(f"Event field '{field}' must be a non-empty str or None")
    return value


def _required_int(*, event: dict[str, object], field: str) -> int:
    value = event.get(field)
    if not isinstance(value, int):
        raise TypeError(f"Event field '{field}' must be an int")
    return value


def _optional_int(*, event: dict[str, object], field: str) -> int | None:
    value = event.get(field)
    if value is None:
        return None
    if not isinstance(value, int):
        raise TypeError(f"Event field '{field}' must be an int or None")
    return value


def _required_float(*, event: dict[str, object], field: str) -> float:
    value = event.get(field)
    if isinstance(value, bool):
        raise TypeError(f"Event field '{field}' must be a float")
    if not isinstance(value, (int, float)):
        raise TypeError(f"Event field '{field}' must be a float")
    return float(value)


def _optional_float(*, event: dict[str, object], field: str) -> float | None:
    value = event.get(field)
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f"Event field '{field}' must be a float or None")
    if not isinstance(value, (int, float)):
        raise TypeError(f"Event field '{field}' must be a float or None")
    return float(value)
