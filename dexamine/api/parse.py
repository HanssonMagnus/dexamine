"""
API entrypoints for parsing by transaction position (block number + tx index).
"""

from __future__ import annotations

from typing import Literal, TypedDict

from dexamine.parsers import uniswap_v2_parser, uniswap_v3_parser
from dexamine.shared import general_helpers

from dexamine.rpc.json_rpc_client import JsonObject, JsonRpcClient


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
EventDict = dict[str, float | int | str | None]


class ParsedPositionResult(TypedDict):
    tx: JsonObject
    receipt: JsonObject
    block: JsonObject
    events: list[EventDict]


def parse_position(
    *,
    node_url: str,
    block_number: int,
    tx_index: int,
    protocol: Protocol,
    exchange_pair_address: str | None,
) -> ParsedPositionResult:
    """
    Fetch raw data for a tx position and parse Uniswap v2/v3 events.

    `exchange_pair_address=None` means "do not filter by pool address".
    """
    raw = parse_position_raw(node_url=node_url, block_number=block_number, tx_index=tx_index)

    receipt = raw["receipt"]
    logs_value = receipt.get("logs")
    if not isinstance(logs_value, list):
        raise TypeError("Receipt is missing 'logs' as a list")
    logs: list[dict[str, object]] = logs_value  # runtime-validated above

    erc20_abi = general_helpers.get_json_abi("erc20/ERC20_abi.json")
    erc20_bytes32_abi = general_helpers.get_json_abi("erc20/ERC20_bytes32_abi.json")

    exchange_pair_address_value = "" if exchange_pair_address is None else exchange_pair_address

    if protocol == "uniswap_v2":
        uniswap_pair_abi = general_helpers.get_json_abi("uniswap_v2/IUniswapV2Pair.json")
        events = uniswap_v2_parser.parse_all_uniswap_v2_events(
            node_url=node_url,
            logs=logs,  # type: ignore[arg-type]
            erc20_abi=erc20_abi,
            erc20_bytes32_abi=erc20_bytes32_abi,
            uniswap_v2_pair_abi=uniswap_pair_abi,
            exchange_pair_address=exchange_pair_address_value,
        )
        return {
            "tx": raw["tx"],
            "receipt": raw["receipt"],
            "block": raw["block"],
            "events": events,
        }

    if protocol == "uniswap_v3":
        uniswap_pair_abi = general_helpers.get_json_abi("uniswap_v3/UniswapV3PoolABI.json")
        parsed = uniswap_v3_parser.parse_all_v3_events(
            node_url=node_url,
            logs=logs,  # type: ignore[arg-type]
            erc20_abi=erc20_abi,
            erc20_bytes32_abi=erc20_bytes32_abi,
            uniswap_v3_pair_abi=uniswap_pair_abi,
            exchange_pair_address=exchange_pair_address_value,
        )
        events = [] if parsed is None else parsed
        return {
            "tx": raw["tx"],
            "receipt": raw["receipt"],
            "block": raw["block"],
            "events": events,
        }

    raise ValueError(f"Unsupported protocol: {protocol}")
