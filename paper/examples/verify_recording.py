"""Check recording identity, historical metadata, and independently decoded amounts."""

import json
import math
from decimal import Decimal, localcontext

from web3 import Web3

from parse_recorded_transaction import BLOCK, TX_INDEX, FIXTURES, parse_example


def verify():
    """Compare public-parser output with the archived RPC responses."""
    raw = {
        name: json.loads((FIXTURES / f"{name}.json").read_text())["result"]
        for name in ("transaction", "receipt", "block")
    }
    tx, receipt, block = (raw[name] for name in ("transaction", "receipt", "block"))
    provenance = json.loads((FIXTURES / "provenance.json").read_text())
    metadata = json.loads((FIXTURES / "metadata.json").read_text())
    assert provenance["chain_id"] == 1
    assert provenance["block_number"] == metadata["block_number"] == BLOCK
    assert provenance["metadata_block_number"] == BLOCK
    assert provenance["transaction_index"] == TX_INDEX
    assert tx["hash"] == receipt["transactionHash"] == provenance["transaction_hash"]
    assert block["transactions"][TX_INDEX] == tx["hash"]
    assert (
        tx["blockHash"]
        == receipt["blockHash"]
        == block["hash"]
        == metadata["block_hash"]
        == provenance["block_hash"]
    )
    assert int(block["number"], 16) == BLOCK
    for source in (tx, receipt):
        assert int(source["blockNumber"], 16) == BLOCK
        assert int(source["transactionIndex"], 16) == TX_INDEX

    recorded = json.loads((FIXTURES / "metadata_rpc.json").read_text())
    results = {response["id"]: response["result"] for response in recorded["responses"]}
    calls = {}
    for query in recorded["requests"]:
        assert query["method"] == "eth_call"
        contract, block_tag = query["params"]
        assert block_tag == hex(BLOCK)
        calls[(contract["to"].lower(), contract["data"])] = results[query["id"]]

    def decode_call(address, signature, abi_type):
        selector = Web3.to_hex(Web3.keccak(text=signature)[:4])
        payload = bytes.fromhex(calls[(address.lower(), selector)][2:])
        return Web3().codec.decode([abi_type], payload)[0]

    for address, token in metadata["erc20"].items():
        assert decode_call(address, "symbol()", "string") == token["symbol"]
        assert decode_call(address, "decimals()", "uint8") == token["decimals"]
    for address, pool in metadata["v3_pools"].items():
        for field in ("token0", "token1", "factory"):
            assert (
                decode_call(address, f"{field}()", "address").lower()
                == pool[field].lower()
            )
        assert pool["factory"].lower() == "0x1f98431c8ad98523631ae4a59f267346ea31f984"
        assert pool["dex_symbol"] == "UniV3"

    rows = parse_example()
    expected = json.loads((FIXTURES.parent / "expected_output.json").read_text())
    assert rows == expected
    signature = Web3.to_hex(
        Web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)")
    )
    indexes = [
        i for i, log in enumerate(receipt["logs"]) if log["topics"][0] == signature
    ]
    assert [row["receipt_log_index"] for row in rows] == indexes == [3, 6, 10, 13]
    for row in rows:
        log = receipt["logs"][row["receipt_log_index"]]
        assert log["transactionHash"] == tx["hash"]
        assert log["blockHash"] == block["hash"]
        pool = metadata["v3_pools"][Web3.to_checksum_address(log["address"])]
        token0, token1 = (metadata["erc20"][pool[key]] for key in ("token0", "token1"))
        assert row["event_type"] == "swap"
        for i, token in enumerate((token0, token1)):
            assert row[f"event_symbol_{i}"] == token["symbol"]
            assert row[f"event_decimals_{i}"] == token["decimals"]
        # Decode signed ABI values independently of dexamine's slicing and floats.
        amount0, amount1, sqrt_x96, liquidity, tick = Web3().codec.decode(
            ["int256", "int256", "uint160", "uint128", "int24"],
            bytes.fromhex(log["data"][2:]),
        )
        assert row["event_tick"] == tick
        with localcontext() as context:
            context.prec = 70
            scale0 = Decimal(10) ** token0["decimals"]
            scale1 = Decimal(10) ** token1["decimals"]
            sqrt_price = Decimal(sqrt_x96) / (2**96)
            values = {
                "amount_0": Decimal(amount0) / scale0,
                "amount_1": Decimal(amount1) / scale1,
                "sqrt_price_x96": Decimal(sqrt_x96),
                "virtual_liquidity": Decimal(liquidity),
                "price": scale1 / scale0 / sqrt_price**2,
                "virtual_reserve_0": Decimal(liquidity) / sqrt_price / scale0,
                "virtual_reserve_1": Decimal(liquidity) * sqrt_price / scale1,
            }
            for field, value in values.items():
                assert math.isclose(
                    row[f"event_{field}"], float(value), rel_tol=1e-12
                ), field
    print(
        "Verified transaction identity, historical metadata, and all four swap states"
    )


if __name__ == "__main__":
    verify()
