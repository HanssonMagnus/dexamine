"""Reproduce the paper example, offline by default, or with --node-url URL."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
from unittest.mock import patch

from dexamine import DexamineSession
from dexamine.metadata import Erc20Metadata, V3PoolMetadata
from dexamine.rpc.json_rpc_client import JsonRpcClient

BLOCK = 12_561_528
TX_INDEX = 31
FIXTURES = Path(__file__).resolve().parent / "data"


def parse_example(node_url=None):
    """Parse all supported v3 events, without a pool filter, in receipt order."""
    session = DexamineSession.from_node_url(node_url or "http://unused.invalid")
    with ExitStack() as stack:
        if node_url is None:
            responses = {
                method: json.loads((FIXTURES / filename).read_text())
                for method, filename in (
                    ("eth_getTransactionByBlockNumberAndIndex", "transaction.json"),
                    ("eth_getTransactionReceipt", "receipt.json"),
                    ("eth_getBlockByNumber", "block.json"),
                )
            }
            tx_hash = responses["eth_getTransactionReceipt"]["result"][
                "transactionHash"
            ]
            expected_params = {
                "eth_getTransactionByBlockNumberAndIndex": [hex(BLOCK), hex(TX_INDEX)],
                "eth_getTransactionReceipt": [tx_hash],
                "eth_getBlockByNumber": [hex(BLOCK), False],
            }

            def replay(_client, method, params, request_id):
                if params != expected_params[method]:
                    raise ValueError("Request does not match the recorded example")
                return responses[method]["result"]

            stack.enter_context(patch.object(JsonRpcClient, "call", replay))
            # Fail immediately if an uncached metadata query attempts network access.
            stack.enter_context(
                patch(
                    "requests.sessions.Session.request",
                    side_effect=RuntimeError("Offline example attempted HTTP"),
                )
            )
            metadata = json.loads((FIXTURES / "metadata.json").read_text())
            session.metadata.seed(
                erc20={
                    address: Erc20Metadata(**values)
                    for address, values in metadata["erc20"].items()
                },
                v3_pools={
                    address: V3PoolMetadata(
                        values["token0"], values["token1"], values["dex_symbol"]
                    )
                    for address, values in metadata["v3_pools"].items()
                },
            )
        rows = session.parse_position(
            block_number=BLOCK,
            tx_index=TX_INDEX,
            protocol="uniswap_v3",
            exchange_pair_address=None,
            output_format="flat",
        )
    return sorted(rows, key=lambda row: row["receipt_log_index"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--node-url", help="Use a live Ethereum endpoint instead of fixtures"
    )
    parser.add_argument(
        "--check", action="store_true", help="Compare with the committed output"
    )
    args = parser.parse_args()
    rows = parse_example(args.node_url)
    rendered = json.dumps(rows, indent=2, allow_nan=False) + "\n"
    if args.check:
        expected = Path(__file__).with_name("expected_output.json").read_text()
        if json.loads(expected) != rows:
            raise SystemExit("Example output differs from expected_output.json")
        print("Four recorded swaps match expected_output.json")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
