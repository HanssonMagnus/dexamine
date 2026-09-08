"""Reproduce the SoftwareX example, offline by default, or with --node-url URL."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import patch

from dexamine import DexamineSession
from dexamine.rpc.json_rpc_client import JsonRpcClient
from dexamine.shared import constants
from dexamine.tests.helpers import make_metadata_resolver

BLOCK = 12_376_729
TX_INDEX = 59
POOL = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
FIXTURES = (
    Path(__file__).resolve().parents[2] / "dexamine/tests/test_data/node_responses"
)


def parse_example(node_url=None):
    """Parse a real v3 mint; replay only the transport and contract metadata offline."""
    session = DexamineSession.from_node_url(node_url or "http://unused.invalid")
    with ExitStack() as stack:
        if node_url is None:
            responses = {
                "eth_getTransactionByBlockNumberAndIndex": json.loads(
                    (FIXTURES / "tx_data.json").read_text()
                ),
                "eth_getTransactionReceipt": json.loads(
                    (FIXTURES / "receipt_data.json").read_text()
                ),
                "eth_getBlockByNumber": json.loads(
                    (FIXTURES / "block_data.json").read_text()
                ),
            }
            tx_hash = responses["eth_getTransactionReceipt"]["result"][
                "transactionHash"
            ]
            expected_params = {
                "eth_getTransactionByBlockNumberAndIndex": [hex(BLOCK), hex(TX_INDEX)],
                "eth_getTransactionReceipt": [tx_hash],
                "eth_getBlockByNumber": [hex(BLOCK), False],
            }

            def replay(_client, payload):
                method = payload["method"]
                if payload["params"] != expected_params[method]:
                    raise ValueError("Request does not match the recorded example")
                return {**responses[method], "id": payload["id"]}

            stack.enter_context(patch.object(JsonRpcClient, "_post", replay))
            # Fail immediately if an uncached metadata query attempts network access.
            stack.enter_context(
                patch(
                    "requests.sessions.Session.request",
                    side_effect=RuntimeError("Offline example attempted HTTP"),
                )
            )
            metadata = make_metadata_resolver(
                erc20={
                    constants.USDC_TOKEN_ADDRESS: ("USDC", 6),
                    constants.WETH_TOKEN_ADDRESS: ("WETH", 18),
                },
                v3_pools={
                    POOL: (
                        constants.USDC_TOKEN_ADDRESS,
                        constants.WETH_TOKEN_ADDRESS,
                        "UniV3",
                    )
                },
            )
            session = replace(session, metadata=metadata)
        return session.parse_position(
            block_number=BLOCK,
            tx_index=TX_INDEX,
            protocol="uniswap_v3",
            exchange_pair_address=POOL,
            output_format="flat",
        )


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
        print("Recorded transaction matches expected_output.json")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
