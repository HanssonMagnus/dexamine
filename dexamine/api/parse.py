"""
API entrypoints for parsing by transaction position (block number + tx index).
"""

from __future__ import annotations

from typing import TypedDict

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
