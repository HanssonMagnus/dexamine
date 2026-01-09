"""
Helpers for converting nested parse results into flat, CSV-friendly rows.

Flat output is designed to be streaming-friendly for very large workloads.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Literal, Mapping, TypedDict

from dexamine.rpc.json_rpc_client import JsonObject
from dexamine.shared.general_helpers import parse_to_type

Protocol = Literal["uniswap_v2", "uniswap_v3"]


class _BaseFlatRow(TypedDict):
    block_timestamp: int
    block_number: int
    block_gas: int
    block_txes: int
    tx_index: int
    log_index: int
    tx_hash: str
    tx_from: str
    tx_to: str | None
    tx_value: int
    tx_gas: int
    tx_gas_price: int | None
    tx_max_priority_fee_per_gas: int | None
    tx_max_fee_per_gas: int | None
    tx_to_type: str


class FlatUniswapV2Row(_BaseFlatRow):
    event_type: str
    event_dex_symbol: str
    event_symbol_0: str
    event_symbol_1: str
    event_decimals_0: int
    event_decimals_1: int
    event_amount_0: float
    event_amount_1: float
    event_amount_0_in: float | None
    event_amount_0_out: float | None
    event_amount_1_in: float | None
    event_amount_1_out: float | None
    event_reserve_0: float
    event_reserve_1: float
    event_mid_price: float
    event_invariant: float


class FlatUniswapV3Row(_BaseFlatRow):
    event_type: str
    event_dex_symbol: str
    event_symbol_0: str
    event_symbol_1: str
    event_decimals_0: int
    event_decimals_1: int
    event_sender: str | None
    event_recipient: str | None
    event_owner: str | None
    event_amount: float | None
    event_amount_0: float
    event_amount_1: float
    event_virtual_liquidity: float | None
    event_tick: int | None
    event_sqrt_price_x96: float | None
    event_price: float | None
    event_tick_lower: int | None
    event_tick_upper: int | None
    event_virtual_reserve_0: float | None
    event_virtual_reserve_1: float | None


FlatRow = FlatUniswapV2Row | FlatUniswapV3Row


FLAT_UNISWAP_V2_COLUMNS: tuple[str, ...] = (
    "block_timestamp",
    "block_number",
    "block_gas",
    "block_txes",
    "tx_index",
    "log_index",
    "tx_hash",
    "tx_from",
    "tx_to",
    "tx_value",
    "tx_gas",
    "tx_gas_price",
    "tx_max_priority_fee_per_gas",
    "tx_max_fee_per_gas",
    "tx_to_type",
    "event_type",
    "event_dex_symbol",
    "event_symbol_0",
    "event_symbol_1",
    "event_decimals_0",
    "event_decimals_1",
    "event_amount_0",
    "event_amount_1",
    "event_amount_0_in",
    "event_amount_0_out",
    "event_amount_1_in",
    "event_amount_1_out",
    "event_reserve_0",
    "event_reserve_1",
    "event_mid_price",
    "event_invariant",
)


FLAT_UNISWAP_V3_COLUMNS: tuple[str, ...] = (
    "block_timestamp",
    "block_number",
    "block_gas",
    "block_txes",
    "tx_index",
    "log_index",
    "tx_hash",
    "tx_from",
    "tx_to",
    "tx_value",
    "tx_gas",
    "tx_gas_price",
    "tx_max_priority_fee_per_gas",
    "tx_max_fee_per_gas",
    "tx_to_type",
    "event_type",
    "event_dex_symbol",
    "event_symbol_0",
    "event_symbol_1",
    "event_decimals_0",
    "event_decimals_1",
    "event_sender",
    "event_recipient",
    "event_owner",
    "event_amount",
    "event_amount_0",
    "event_amount_1",
    "event_virtual_liquidity",
    "event_tick",
    "event_sqrt_price_x96",
    "event_price",
    "event_tick_lower",
    "event_tick_upper",
    "event_virtual_reserve_0",
    "event_virtual_reserve_1",
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


def _parse_block_timestamp(*, block: JsonObject) -> int:
    return _parse_hex_int(value=block.get("timestamp"), field_name="block.timestamp")


def _parse_block_gas_used(*, block: JsonObject) -> int:
    return _parse_hex_int(value=block.get("gasUsed"), field_name="block.gasUsed")


def _parse_block_txes(*, block: JsonObject) -> int:
    txes_value = block.get("transactions")
    if not isinstance(txes_value, list):
        raise TypeError("block.transactions must be a list")
    return len(txes_value)


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
) -> _BaseFlatRow:
    to_address = _tx_to(tx=tx)
    return {
        "block_timestamp": _parse_block_timestamp(block=block),
        "block_number": block_number,
        "block_gas": _parse_block_gas_used(block=block),
        "block_txes": _parse_block_txes(block=block),
        "tx_index": tx_index,
        "log_index": -1,  # populated per event (aka log index)
        "tx_hash": _tx_hash(tx=tx),
        "tx_from": _tx_from(tx=tx),
        "tx_to": to_address,
        "tx_value": _tx_value(tx=tx),
        "tx_gas": _tx_gas(tx=tx),
        "tx_gas_price": _tx_gas_price(tx=tx, receipt=receipt),
        "tx_max_priority_fee_per_gas": _tx_max_priority_fee(tx=tx),
        "tx_max_fee_per_gas": _tx_max_fee(tx=tx),
        "tx_to_type": parse_to_type(to_address),
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
                "log_index": event_index_value,
                "event_type": _required_str(event=event, field="event_type"),
                "event_dex_symbol": _required_str(event=event, field="dex_symbol"),
                "event_symbol_0": _required_str(event=event, field="symbol_0"),
                "event_symbol_1": _required_str(event=event, field="symbol_1"),
                "event_decimals_0": _required_int(event=event, field="decimals_0"),
                "event_decimals_1": _required_int(event=event, field="decimals_1"),
                "event_amount_0": _required_float(event=event, field="amount_0"),
                "event_amount_1": _required_float(event=event, field="amount_1"),
                "event_amount_0_in": _optional_float(event=event, field="amount_0_in"),
                "event_amount_0_out": _optional_float(
                    event=event, field="amount_0_out"
                ),
                "event_amount_1_in": _optional_float(event=event, field="amount_1_in"),
                "event_amount_1_out": _optional_float(
                    event=event, field="amount_1_out"
                ),
                "event_reserve_0": _required_float(event=event, field="reserve_0"),
                "event_reserve_1": _required_float(event=event, field="reserve_1"),
                "event_mid_price": _required_float(event=event, field="mid_price"),
                "event_invariant": _required_float(event=event, field="invariant"),
            }
            yield row
        return

    if protocol == "uniswap_v3":
        for event in events:
            event_index_value = event.get("event_index")
            if not isinstance(event_index_value, int):
                raise TypeError("Uniswap v3 event is missing 'event_index' as int")

            row_v3: FlatUniswapV3Row = {
                **base,
                "log_index": event_index_value,
                "event_type": _required_str(event=event, field="event_type"),
                "event_dex_symbol": _required_str(event=event, field="dex_symbol"),
                "event_symbol_0": _required_str(event=event, field="symbol_0"),
                "event_symbol_1": _required_str(event=event, field="symbol_1"),
                "event_decimals_0": _required_int(event=event, field="decimals_0"),
                "event_decimals_1": _required_int(event=event, field="decimals_1"),
                "event_sender": _optional_str(event=event, field="sender"),
                "event_recipient": _optional_str(event=event, field="recipient"),
                "event_owner": _optional_str(event=event, field="owner"),
                "event_amount": _optional_float(event=event, field="amount"),
                "event_amount_0": _required_float(event=event, field="amount_0"),
                "event_amount_1": _required_float(event=event, field="amount_1"),
                "event_virtual_liquidity": _optional_float(
                    event=event, field="virtual_liquidity"
                ),
                "event_tick": _optional_int(event=event, field="tick"),
                "event_sqrt_price_x96": _optional_float(
                    event=event, field="sqrt_price_x96"
                ),
                "event_price": _optional_float(event=event, field="price"),
                "event_tick_lower": _optional_int(event=event, field="tick_lower"),
                "event_tick_upper": _optional_int(event=event, field="tick_upper"),
                "event_virtual_reserve_0": _optional_float(
                    event=event, field="virtual_reserve_0"
                ),
                "event_virtual_reserve_1": _optional_float(
                    event=event, field="virtual_reserve_1"
                ),
            }
            yield row_v3
        return

    raise ValueError(f"Unsupported protocol: {protocol}")


def _required_str(*, event: Mapping[str, object], field: str) -> str:
    value = event.get(field)
    if not isinstance(value, str) or not value:
        raise TypeError(f"Event field '{field}' must be a non-empty str")
    return value


def _optional_str(*, event: Mapping[str, object], field: str) -> str | None:
    value = event.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise TypeError(f"Event field '{field}' must be a non-empty str or None")
    return value


def _required_int(*, event: Mapping[str, object], field: str) -> int:
    value = event.get(field)
    if not isinstance(value, int):
        raise TypeError(f"Event field '{field}' must be an int")
    return value


def _optional_int(*, event: Mapping[str, object], field: str) -> int | None:
    value = event.get(field)
    if value is None:
        return None
    if not isinstance(value, int):
        raise TypeError(f"Event field '{field}' must be an int or None")
    return value


def _required_float(*, event: Mapping[str, object], field: str) -> float:
    value = event.get(field)
    if isinstance(value, bool):
        raise TypeError(f"Event field '{field}' must be a float")
    if not isinstance(value, (int, float)):
        raise TypeError(f"Event field '{field}' must be a float")
    return float(value)


def _optional_float(*, event: Mapping[str, object], field: str) -> float | None:
    value = event.get(field)
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f"Event field '{field}' must be a float or None")
    if not isinstance(value, (int, float)):
        raise TypeError(f"Event field '{field}' must be a float or None")
    return float(value)
