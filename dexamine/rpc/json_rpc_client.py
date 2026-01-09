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
            logger.error(
                "JSON-RPC request failed", extra={"payload": payload}, exc_info=True
            )
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

    def _post_batch(self, payload: list[JsonObject]) -> list[JsonObject]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        timeout_seconds = 30
        try:
            response = requests.post(
                self.node_url, headers=headers, json=payload, timeout=timeout_seconds
            )
        except requests.RequestException as exc:
            logger.error(
                "JSON-RPC batch request failed",
                extra={"payload_len": len(payload)},
                exc_info=True,
            )
            raise ConnectionError(f"JSON-RPC batch request failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                "JSON-RPC batch response is not valid JSON",
                extra={"payload_len": len(payload), "status_code": response.status_code},
                exc_info=True,
            )
            raise JsonRpcResponseFormatError(
                "JSON-RPC batch response is not valid JSON"
            ) from exc

        if not isinstance(data, list):
            raise JsonRpcResponseFormatError(
                f"JSON-RPC batch response must be a list, got {type(data)}"
            )

        out: list[JsonObject] = []
        for item in data:
            if not isinstance(item, dict):
                raise JsonRpcResponseFormatError(
                    f"JSON-RPC batch response items must be objects, got {type(item)}"
                )
            out.append(item)  # type: ignore[arg-type]

        return out

    def batch_call(self, calls: list[tuple[str, JsonArray, int]]) -> dict[int, JsonValue]:
        """
        Execute a JSON-RPC batch request.

        Args:
            calls: List of (method, params, request_id).

        Returns:
            Dict mapping request_id -> result.
        """
        payload: list[JsonObject] = []
        for method, params, request_id in calls:
            payload.append(
                {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": request_id,
                }
            )

        responses = self._post_batch(payload)
        by_id: dict[int, JsonValue] = {}

        for resp in responses:
            response_id = resp.get("id")
            if not isinstance(response_id, int):
                raise JsonRpcResponseFormatError(
                    f"JSON-RPC batch response missing int 'id', got {response_id}"
                )

            if "error" in resp and resp["error"] is not None:
                raise JsonRpcError(f"JSON-RPC error (id={response_id}): {resp['error']}")

            if "result" not in resp:
                raise JsonRpcResponseFormatError(
                    f"JSON-RPC batch response missing 'result' (id={response_id})"
                )

            by_id[response_id] = resp["result"]

        return by_id

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
            raise JsonRpcResultNotFoundError(
                f"Block not found for block_number={block_number}"
            )
        if not isinstance(result, dict):
            raise JsonRpcResponseFormatError(
                f"Block result must be an object, got {type(result)}"
            )
        return result  # type: ignore[return-value]
