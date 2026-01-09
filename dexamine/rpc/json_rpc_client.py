"""
Minimal JSON-RPC client used by dexamine.

This module intentionally keeps the surface small and explicit so it can be reused
from multiprocessing workers without hidden global state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Union

import requests

logger = logging.getLogger(__name__)

JsonScalar = Union[str, int, float, bool, None]
JsonValue = Union[JsonScalar, "JsonObject", "JsonArray"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]


class JsonRpcError(RuntimeError):
    """Raised when the JSON-RPC node returns an error payload."""


class JsonRpcResponseFormatError(ValueError):
    """Raised when the JSON-RPC response payload is not in an expected format."""


class JsonRpcResultNotFoundError(LookupError):
    """Raised when a JSON-RPC method returns result=None for a requested item."""


def to_hex_quantity(value: int) -> str:
    """
    Convert a non-negative integer to an Ethereum JSON-RPC quantity hex string.

    Example: 15 -> "0xf"
    """
    if value < 0:
        raise ValueError(f"value must be >= 0, got {value}")
    return hex(value)


@dataclass(frozen=True, slots=True)
class JsonRpcClient:
    node_url: str

    def _post(self, payload: JsonObject) -> JsonObject:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        timeout_seconds = 30
        try:
            response = requests.post(
                self.node_url, headers=headers, json=payload, timeout=timeout_seconds
            )
        except requests.RequestException as exc:
            logger.error("JSON-RPC request failed", extra={"payload": payload}, exc_info=True)
            raise ConnectionError(f"JSON-RPC request failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "JSON-RPC response is not valid JSON",
                extra={"payload": payload, "status_code": response.status_code},
                exc_info=True,
            )
            raise JsonRpcResponseFormatError(
                "JSON-RPC response is not valid JSON"
            ) from exc

        if not isinstance(data, dict):
            raise JsonRpcResponseFormatError(
                f"JSON-RPC response must be an object, got {type(data)}"
            )
        return data  # type: ignore[return-value]

    def call(self, method: str, params: JsonArray, request_id: int) -> JsonValue:
        payload: JsonObject = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id,
        }
        data = self._post(payload)

        if "error" in data and data["error"] is not None:
            raise JsonRpcError(f"JSON-RPC error: {data['error']}")

        if "result" not in data:
            raise JsonRpcResponseFormatError("JSON-RPC response missing 'result'")

        return data["result"]

    def get_transaction_by_block_number_and_index(
        self, block_number: int, tx_index: int, request_id: int
    ) -> JsonObject:
        block_hex = to_hex_quantity(block_number)
        index_hex = to_hex_quantity(tx_index)
        result = self.call(
            "eth_getTransactionByBlockNumberAndIndex",
            params=[block_hex, index_hex],
            request_id=request_id,
        )
        if result is None:
            raise JsonRpcResultNotFoundError(
                f"Transaction not found for block_number={block_number}, tx_index={tx_index}"
            )
        if not isinstance(result, dict):
            raise JsonRpcResponseFormatError(
                f"Transaction result must be an object, got {type(result)}"
            )
        return result  # type: ignore[return-value]

    def get_transaction_receipt(self, tx_hash: str, request_id: int) -> JsonObject:
        result = self.call(
            "eth_getTransactionReceipt", params=[tx_hash], request_id=request_id
        )
        if result is None:
            raise JsonRpcResultNotFoundError(f"Receipt not found for tx_hash={tx_hash}")
        if not isinstance(result, dict):
            raise JsonRpcResponseFormatError(
                f"Receipt result must be an object, got {type(result)}"
            )
        return result  # type: ignore[return-value]

    def get_block_by_number(
        self, block_number: int, include_transactions: bool, request_id: int
    ) -> JsonObject:
        block_hex = to_hex_quantity(block_number)
        result = self.call(
            "eth_getBlockByNumber",
            params=[block_hex, include_transactions],
            request_id=request_id,
        )
        if result is None:
            raise JsonRpcResultNotFoundError(f"Block not found for block_number={block_number}")
        if not isinstance(result, dict):
            raise JsonRpcResponseFormatError(
                f"Block result must be an object, got {type(result)}"
            )
        return result  # type: ignore[return-value]

