"""
Session-style API for reusing resources across many calls.

This is a connector class (allowed to hold state) that is safe to instantiate per
process when using multiprocessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Literal

from dexamine.api.flat_output import FlatRow, iter_flat_rows
from dexamine.parsers import uniswap_v2_parser, uniswap_v3_parser
from dexamine.metadata.resolver import MetadataResolver
from dexamine.rpc.json_rpc_client import JsonObject, JsonRpcClient, to_hex_quantity
from dexamine.shared import general_helpers

Protocol = Literal["uniswap_v2", "uniswap_v3"]
OutputFormat = Literal["raw", "flat"]
EventDict = dict[str, float | int | str | None]


def _chunked_positions(
    positions: Iterable[tuple[int, int]], chunk_size: int
) -> Iterator[list[tuple[int, int]]]:
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be > 0, got {chunk_size}")

    chunk: list[tuple[int, int]] = []
    for item in positions:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


@dataclass(frozen=True, slots=True)
class DexamineSession:
    node_url: str
    rpc: JsonRpcClient
    erc20_abi: dict
    erc20_bytes32_abi: dict
    uniswap_v2_pair_abi: dict
    uniswap_v3_pair_abi: dict
    metadata: MetadataResolver

    @classmethod
    def from_node_url(cls, node_url: str) -> "DexamineSession":
        rpc = JsonRpcClient(node_url=node_url)
        erc20_abi = general_helpers.get_json_abi("erc20/ERC20_abi.json")
        erc20_bytes32_abi = general_helpers.get_json_abi("erc20/ERC20_bytes32_abi.json")
        uniswap_v2_pair_abi = general_helpers.get_json_abi(
            "uniswap_v2/IUniswapV2Pair.json"
        )
        uniswap_v3_pair_abi = general_helpers.get_json_abi(
            "uniswap_v3/UniswapV3PoolABI.json"
        )
        metadata = MetadataResolver(
            node_url=node_url,
            erc20_abi=erc20_abi,
            erc20_bytes32_abi=erc20_bytes32_abi,
            uniswap_v2_pair_abi=uniswap_v2_pair_abi,
            uniswap_v3_pair_abi=uniswap_v3_pair_abi,
        )
        return cls(
            node_url=node_url,
            rpc=rpc,
            erc20_abi=erc20_abi,
            erc20_bytes32_abi=erc20_bytes32_abi,
            uniswap_v2_pair_abi=uniswap_v2_pair_abi,
            uniswap_v3_pair_abi=uniswap_v3_pair_abi,
            metadata=metadata,
        )

    def parse_position_raw(
        self, *, block_number: int, tx_index: int
    ) -> dict[str, JsonObject]:
        tx = self.rpc.get_transaction_by_block_number_and_index(
            block_number=block_number, tx_index=tx_index, request_id=1
        )
        tx_hash_value = tx.get("hash")
        if not isinstance(tx_hash_value, str) or not tx_hash_value:
            raise ValueError("Transaction is missing a valid 'hash' field")

        receipt = self.rpc.get_transaction_receipt(tx_hash=tx_hash_value, request_id=2)
        block = self.rpc.get_block_by_number(
            block_number=block_number, include_transactions=False, request_id=3
        )

        return {"tx": tx, "receipt": receipt, "block": block}

    def parse_position(
        self,
        *,
        block_number: int,
        tx_index: int,
        protocol: Protocol,
        exchange_pair_address: str | None,
        output_format: OutputFormat = "raw",
    ) -> dict[str, object] | list[FlatRow]:
        raw = self.parse_position_raw(block_number=block_number, tx_index=tx_index)

        receipt = raw["receipt"]
        logs_value = receipt.get("logs")
        if not isinstance(logs_value, list):
            raise TypeError("Receipt is missing 'logs' as a list")

        exchange_pair_address_value = (
            "" if exchange_pair_address is None else exchange_pair_address
        )

        if protocol == "uniswap_v2":
            events = uniswap_v2_parser.parse_all_uniswap_v2_events(
                node_url=self.node_url,
                metadata_resolver=self.metadata,
                logs=logs_value,  # type: ignore[arg-type]
                erc20_abi=self.erc20_abi,
                erc20_bytes32_abi=self.erc20_bytes32_abi,
                uniswap_v2_pair_abi=self.uniswap_v2_pair_abi,
                exchange_pair_address=exchange_pair_address_value,
            )
            if output_format == "raw":
                return {**raw, "events": events}

            return list(
                iter_flat_rows(
                    protocol=protocol,
                    tx=raw["tx"],
                    receipt=raw["receipt"],
                    block=raw["block"],
                    block_number=block_number,
                    tx_index=tx_index,
                    events=events,
                )
            )

        if protocol == "uniswap_v3":
            parsed = uniswap_v3_parser.parse_all_v3_events(
                node_url=self.node_url,
                metadata_resolver=self.metadata,
                logs=logs_value,  # type: ignore[arg-type]
                erc20_abi=self.erc20_abi,
                erc20_bytes32_abi=self.erc20_bytes32_abi,
                uniswap_v3_pair_abi=self.uniswap_v3_pair_abi,
                exchange_pair_address=exchange_pair_address_value,
            )
            events = [] if parsed is None else parsed
            if output_format == "raw":
                return {**raw, "events": events}

            return list(
                iter_flat_rows(
                    protocol=protocol,
                    tx=raw["tx"],
                    receipt=raw["receipt"],
                    block=raw["block"],
                    block_number=block_number,
                    tx_index=tx_index,
                    events=events,
                )
            )

        raise ValueError(f"Unsupported protocol: {protocol}")

    def parse_positions(
        self,
        *,
        positions: Iterable[tuple[int, int]],
        protocol: Protocol,
        exchange_pair_address: str | None,
        batch_size: int,
        output_format: OutputFormat = "raw",
    ) -> Iterator[dict[str, object] | FlatRow]:
        """
        Parse many tx positions efficiently using JSON-RPC batching.

        Notes:
        - This yields results incrementally to avoid holding all results in memory.
        - Errors are fail-fast (first invalid/missing result raises).
        """
        for chunk in _chunked_positions(positions=positions, chunk_size=batch_size):
            # 1) Fetch transactions by (block_number, tx_index)
            tx_calls: list[tuple[str, list[object], int]] = []
            for i, (block_number, tx_index) in enumerate(chunk, start=1):
                tx_calls.append(
                    (
                        "eth_getTransactionByBlockNumberAndIndex",
                        [to_hex_quantity(block_number), to_hex_quantity(tx_index)],
                        i,
                    )
                )

            tx_results = self.rpc.batch_call(tx_calls)

            # 2) Fetch receipts by tx hash
            receipt_calls: list[tuple[str, list[object], int]] = []
            tx_by_pos: dict[tuple[int, int], JsonObject] = {}
            tx_hash_by_pos: dict[tuple[int, int], str] = {}

            for i, pos in enumerate(chunk, start=1):
                tx_value = tx_results.get(i)
                if not isinstance(tx_value, dict):
                    raise TypeError(
                        f"Transaction result must be an object, got {type(tx_value)}"
                    )
                tx: JsonObject = tx_value  # runtime-validated above

                tx_hash_value = tx.get("hash")
                if not isinstance(tx_hash_value, str) or not tx_hash_value:
                    raise ValueError(f"Transaction missing 'hash' for position={pos}")

                tx_by_pos[pos] = tx
                tx_hash_by_pos[pos] = tx_hash_value
                receipt_calls.append(("eth_getTransactionReceipt", [tx_hash_value], i))

            receipt_results = self.rpc.batch_call(receipt_calls)

            # 3) Fetch blocks once per unique block number
            unique_blocks: list[int] = sorted(
                {block_number for block_number, _ in chunk}
            )
            block_id_by_number: dict[int, int] = {}
            block_calls: list[tuple[str, list[object], int]] = []
            for i, block_number in enumerate(unique_blocks, start=1):
                block_id_by_number[block_number] = i
                block_calls.append(
                    (
                        "eth_getBlockByNumber",
                        [to_hex_quantity(block_number), False],
                        i,
                    )
                )

            block_results = self.rpc.batch_call(block_calls)
            block_by_number: dict[int, JsonObject] = {}
            for block_number, request_id in block_id_by_number.items():
                block_value = block_results.get(request_id)
                if not isinstance(block_value, dict):
                    raise TypeError(
                        f"Block result must be an object, got {type(block_value)}"
                    )
                block_by_number[block_number] = block_value  # type: ignore[assignment]

            # 4) Parse logs for each position
            for i, pos in enumerate(chunk, start=1):
                block_number, tx_index = pos
                receipt_value = receipt_results.get(i)
                if not isinstance(receipt_value, dict):
                    raise TypeError(
                        f"Receipt result must be an object, got {type(receipt_value)}"
                    )
                receipt: JsonObject = receipt_value  # runtime-validated above

                logs_value = receipt.get("logs")
                if not isinstance(logs_value, list):
                    raise TypeError(f"Receipt missing 'logs' list for position={pos}")

                exchange_pair_address_value = (
                    "" if exchange_pair_address is None else exchange_pair_address
                )

                if protocol == "uniswap_v2":
                    events = uniswap_v2_parser.parse_all_uniswap_v2_events(
                        node_url=self.node_url,
                        metadata_resolver=self.metadata,
                        logs=logs_value,  # type: ignore[arg-type]
                        erc20_abi=self.erc20_abi,
                        erc20_bytes32_abi=self.erc20_bytes32_abi,
                        uniswap_v2_pair_abi=self.uniswap_v2_pair_abi,
                        exchange_pair_address=exchange_pair_address_value,
                    )
                    tx = tx_by_pos[pos]
                    block = block_by_number[block_number]
                    if output_format == "raw":
                        yield {
                            "tx": tx,
                            "receipt": receipt,
                            "block": block,
                            "events": events,
                        }
                        continue

                    yield from iter_flat_rows(
                        protocol=protocol,
                        tx=tx,
                        receipt=receipt,
                        block=block,
                        block_number=block_number,
                        tx_index=tx_index,
                        events=events,
                    )
                    continue

                if protocol == "uniswap_v3":
                    parsed = uniswap_v3_parser.parse_all_v3_events(
                        node_url=self.node_url,
                        metadata_resolver=self.metadata,
                        logs=logs_value,  # type: ignore[arg-type]
                        erc20_abi=self.erc20_abi,
                        erc20_bytes32_abi=self.erc20_bytes32_abi,
                        uniswap_v3_pair_abi=self.uniswap_v3_pair_abi,
                        exchange_pair_address=exchange_pair_address_value,
                    )
                    events = [] if parsed is None else parsed
                    tx = tx_by_pos[pos]
                    block = block_by_number[block_number]
                    if output_format == "raw":
                        yield {
                            "tx": tx,
                            "receipt": receipt,
                            "block": block,
                            "events": events,
                        }
                        continue

                    yield from iter_flat_rows(
                        protocol=protocol,
                        tx=tx,
                        receipt=receipt,
                        block=block,
                        block_number=block_number,
                        tx_index=tx_index,
                        events=events,
                    )
                    continue

                raise ValueError(f"Unsupported protocol: {protocol}")
