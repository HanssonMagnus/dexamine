# API

`dexamine` exposes session and parsing entrypoints from the top-level package:

```python
from dexamine import DexamineSession, parse_position, parse_position_raw, parse_positions
```

- `parse_position` — parse one `(block_number, tx_index)` position.
- `parse_positions` — parse many positions (a convenience wrapper that materializes a
  list; prefer `DexamineSession` for large workloads).
- `parse_position_raw` — fetch the transaction, receipt and block without parsing.
- `DexamineSession` — reuses ABIs and caches pool and token metadata across calls.

See also [Installation](./installation.md) and
[Scope and limitations](./limitations.md).

## Supply recorded metadata

Starting with version 1.1.0, `MetadataResolver.seed` accepts mappings of token or pool
addresses to immutable metadata objects. For example:

```python
from dexamine import DexamineSession
from dexamine.metadata import Erc20Metadata, V3PoolMetadata

session = DexamineSession.from_node_url("http://localhost:8545")
usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
pool = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
session.metadata.seed(
    erc20={usdc: Erc20Metadata("USDC", 6), weth: Erc20Metadata("WETH", 18)},
    v3_pools={pool: V3PoolMetadata(usdc, weth, "UniV3")},
)
```

For Uniswap v2, use `v2_pairs={address: V2PairMetadata(token0, token1, dex_symbol)}`;
`V2PairMetadata` and `MetadataResolver` are also exported from `dexamine.metadata`.

Seeding makes no network requests. It normalizes cache keys and pool token addresses
to checksum form and copies the supplied mappings. Supplied entries overwrite
existing values; omitted entries are retained. Invalid addresses raise `ValueError`
before any cache is changed. The caller is responsible for metadata accuracy and for
retaining its source and date or block context.

A cache miss still queries the configured endpoint. Seeding metadata alone does not
make transaction retrieval work offline. The [recorded example](../paper/examples/README.md)
also replays RPC results and rejects unexpected HTTP access.

## Errors

- `JsonRpcResultNotFoundError` — the node answered with `null` for a transaction,
  receipt or block. The message names the position that could not be fetched. Usually
  means the position does not exist, or the endpoint has pruned that history.
- `JsonRpcError` — the node returned an error object (rate limits, pruned history).
- `JsonRpcResponseFormatError` — the response was not in the expected shape.
The three above are importable from `dexamine.rpc.json_rpc_client`;
`JsonRpcResultNotFoundError` subclasses `LookupError`, `JsonRpcError` subclasses
`RuntimeError`, and `JsonRpcResponseFormatError` subclasses `ValueError`.

A plain `ValueError` is raised for an unsupported `protocol`, a non-positive
`batch_size`, or a transaction the node returned without a usable `hash`.

## Parse a single transaction position

```python
from dexamine import parse_position

result = parse_position(
    node_url="http://localhost:8545",
    block_number=10008555,
    tx_index=25,
    protocol="uniswap_v2",
    exchange_pair_address=None,
)

events = result["events"]
```

## Parse many positions (batched)

For high throughput, use a session and stream results:

```python
from dexamine import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")

positions = [(10008555, 25), (10008566, 1)]

for parsed in session.parse_positions(
    positions=positions,
    protocol="uniswap_v2",
    exchange_pair_address=None,
    batch_size=2000,
):
    # parsed = {"tx", "receipt", "block", "events"}
    pass
```

## Flat output (`output_format="flat"`) for CSV export

Use `output_format="flat"` to get a CSV-friendly stream of **one row per parsed event**.

Note: flat output is **opinionated** (selected fields only; not the full raw payload).
Also note that `DexamineSession.parse_positions(...)` is a generator; it is intended to
be consumed as a stream for large workloads.

```python
from dexamine import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")
rows = session.parse_positions(
    positions=[(10008555, 25), (10008566, 1)],
    protocol="uniswap_v2",
    exchange_pair_address=None,
    batch_size=2000,
    output_format="flat",
)

# For small experiments only:
rows_list = list(rows)
```

## Flat output columns

Flat output rows are built from the raw payload parts:

- `block`: block object returned by JSON-RPC (e.g. `eth_getBlockByNumber`)
- `tx`: transaction object returned by JSON-RPC (e.g. `eth_getTransactionByBlockNumberAndIndex`)
- `receipt`: receipt object returned by JSON-RPC (e.g. `eth_getTransactionReceipt`)
- `event`: a parsed event emitted by the DEX parser

All hex quantities are converted to Python `int` in `flat`. Unless otherwise noted,
fee-related fields are in **wei** and timestamps are Unix seconds.

### Shared columns (all protocols)

- `block_timestamp`: from `block.timestamp`
- `block_number`: the block number passed to the API (matches `block.number`)
- `block_base_fee_per_gas`: from `block.baseFeePerGas` (EIP-1559; `None` if missing)
- `block_gas_limit`: from `block.gasLimit`
- `block_gas_used`: from `block.gasUsed`
- `block_transactions_count`: `len(block.transactions)` (block was fetched with `include_transactions=False`)
- `tx_index`: the transaction index passed to the API (matches `tx.transactionIndex`)
- `receipt_log_index`: index into `receipt.logs` for the parsed event (one row per event)
- `tx_hash`: from `tx.hash`
- `tx_from`: from `tx.from`
- `tx_to`: from `tx.to` (`None` for contract creation)
- `tx_value`: from `tx.value`
- `tx_gas`: from `tx.gas` (gas limit)
- `tx_gas_price`: from `tx.gasPrice` (`None` if missing; typically legacy transactions)
- `receipt_gas_used`: from `receipt.gasUsed` (`None` if missing)
- `receipt_effective_gas_price`: from `receipt.effectiveGasPrice` (`None` if missing; may fall back to `tx.gasPrice`)
- `tx_max_priority_fee_per_gas`: from `tx.maxPriorityFeePerGas` (`None` if missing)
- `tx_max_fee_per_gas`: from `tx.maxFeePerGas` (`None` if missing)
- `tx_type`: from `tx.type` (EIP-2718; `None` if missing)
- `tx_to_type`: routing classification derived from `tx_to`
  (see `dexamine/shared/general_helpers.py:parse_to_type`). One of:
  - `uniswap_router`: sent directly to a canonical Uniswap router or periphery contract
    (the deployments listed in `dexamine/shared/constants.py:uniswap_address_list`)
  - `other_contract`: routed through any other contract (aggregator, arbitrage bot, or
    another DeFi protocol)
  - `contract_creation`: `tx_to` is `None`

  The classification uses protocol constants only. It deliberately does not depend on
  curated third-party label sets (for example Etherscan account labels), so the output
  is deterministic and stable over time. Finer attribution of `other_contract`
  transactions is left to the user.

### Protocol-specific `event_*` columns

Event columns depend on the chosen protocol:

- Uniswap v2: see `docs/parsers/uniswap_v2.md`
- Uniswap v3: see `docs/parsers/uniswap_v3.md`

## Multiprocessing

For million-scale workloads, shard `positions` across processes. Create one
`DexamineSession` per worker process.
