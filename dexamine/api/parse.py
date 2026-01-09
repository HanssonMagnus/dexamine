"""
API entrypoints for parsing by transaction position (block number + tx index).
"""

from __future__ import annotations

from typing import Literal, TypedDict, overload

from dexamine.api.flat_output import FlatRow
from dexamine.rpc.json_rpc_client import JsonObject, JsonRpcClient
from dexamine.api.session import DexamineSession


class RawPositionResult(TypedDict):
    tx: JsonObject
    receipt: JsonObject
    block: JsonObject


def parse_position_raw(
    node_url: str, block_number: int, tx_index: int
) -> RawPositionResult:
    """
    Fetch raw transaction, receipt, and block data for a tx position.

    This is the minimal building block for higher-level parsing and is designed to be
    multiprocessing-friendly (no shared globals).
    """
    client = JsonRpcClient(node_url=node_url)

    tx = client.get_transaction_by_block_number_and_index(
        block_number=block_number, tx_index=tx_index, request_id=1
    )
    tx_hash_value = tx.get("hash")
    if not isinstance(tx_hash_value, str) or not tx_hash_value:
        raise ValueError("Transaction is missing a valid 'hash' field")

    receipt = client.get_transaction_receipt(tx_hash=tx_hash_value, request_id=2)
    block = client.get_block_by_number(
        block_number=block_number, include_transactions=False, request_id=3
    )

    return {"tx": tx, "receipt": receipt, "block": block}


Protocol = Literal["uniswap_v2", "uniswap_v3"]
OutputFormat = Literal["raw", "flat"]
EventDict = dict[str, float | int | str | None]


class ParsedPositionResult(TypedDict):
    tx: JsonObject
    receipt: JsonObject
    block: JsonObject
    events: list[EventDict]


@overload
def parse_positions(
    *,
    node_url: str,
    positions: list[tuple[int, int]],
    protocol: Protocol,
    exchange_pair_address: str | None,
    batch_size: int,
    output_format: Literal["raw"] = "raw",
) -> list[dict[str, object]]: ...


@overload
def parse_positions(
    *,
    node_url: str,
    positions: list[tuple[int, int]],
    protocol: Protocol,
    exchange_pair_address: str | None,
    batch_size: int,
    output_format: Literal["flat"],
) -> list[FlatRow]: ...


def parse_positions(
    *,
    node_url: str,
    positions: list[tuple[int, int]],
    protocol: Protocol,
    exchange_pair_address: str | None,
    batch_size: int,
    output_format: OutputFormat = "raw",
) -> list[dict[str, object]] | list[FlatRow]:
    """
    Convenience wrapper around DexamineSession.parse_positions(...).

    For very large workloads, prefer creating a DexamineSession once and iterating
    the generator returned by session.parse_positions(...).
    """
    session = DexamineSession.from_node_url(node_url)
    return list(
        session.parse_positions(
            positions=positions,
            protocol=protocol,
            exchange_pair_address=exchange_pair_address,
            batch_size=batch_size,
            output_format=output_format,
        )
    )


@overload
def parse_position(
    *,
    node_url: str,
    block_number: int,
    tx_index: int,
    protocol: Protocol,
    exchange_pair_address: str | None,
    output_format: Literal["raw"] = "raw",
) -> ParsedPositionResult: ...


@overload
def parse_position(
    *,
    node_url: str,
    block_number: int,
    tx_index: int,
    protocol: Protocol,
    exchange_pair_address: str | None,
    output_format: Literal["flat"],
) -> list[FlatRow]: ...


def parse_position(
    *,
    node_url: str,
    block_number: int,
    tx_index: int,
    protocol: Protocol,
    exchange_pair_address: str | None,
    output_format: OutputFormat = "raw",
) -> ParsedPositionResult | list[FlatRow]:
    """
    Fetch raw data for a tx position and parse Uniswap v2/v3 events.

    `exchange_pair_address=None` means "do not filter by pool address".
    """
    session = DexamineSession.from_node_url(node_url)
    result = session.parse_position(
        block_number=block_number,
        tx_index=tx_index,
        protocol=protocol,
        exchange_pair_address=exchange_pair_address,
        output_format=output_format,
    )

    if output_format == "flat":
        if not isinstance(result, list):
            raise TypeError("Expected flat output as a list of rows")
        return result

    return {
        "tx": result["tx"],  # type: ignore[typeddict-item]
        "receipt": result["receipt"],  # type: ignore[typeddict-item]
        "block": result["block"],  # type: ignore[typeddict-item]
        "events": result["events"],  # type: ignore[typeddict-item]
    }
