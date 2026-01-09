"""
Session-style API for reusing resources across many calls.

This is a connector class (allowed to hold state) that is safe to instantiate per
process when using multiprocessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from dexamine.parsers import uniswap_v2_parser, uniswap_v3_parser
from dexamine.metadata.resolver import MetadataResolver
from dexamine.rpc.json_rpc_client import JsonObject, JsonRpcClient
from dexamine.shared import general_helpers

Protocol = Literal["uniswap_v2", "uniswap_v3"]
EventDict = dict[str, float | int | str | None]


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
        uniswap_v2_pair_abi = general_helpers.get_json_abi("uniswap_v2/IUniswapV2Pair.json")
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

    def parse_position_raw(self, *, block_number: int, tx_index: int) -> dict[str, JsonObject]:
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
    ) -> dict[str, object]:
        raw = self.parse_position_raw(block_number=block_number, tx_index=tx_index)

        receipt = raw["receipt"]
        logs_value = receipt.get("logs")
        if not isinstance(logs_value, list):
            raise TypeError("Receipt is missing 'logs' as a list")

        exchange_pair_address_value = "" if exchange_pair_address is None else exchange_pair_address

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
            return {**raw, "events": events}

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
            return {**raw, "events": events}

        raise ValueError(f"Unsupported protocol: {protocol}")

