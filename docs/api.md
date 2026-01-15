# API

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
from dexamine.api.session import DexamineSession

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
from dexamine.api.session import DexamineSession

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
- `tx_to_type`: derived from `tx_to` (see `dexamine/shared/general_helpers.py:parse_to_type`)

### Protocol-specific `event_*` columns

Event columns depend on the chosen protocol:

- Uniswap v2: see `docs/parsers/uniswap_v2.md`
- Uniswap v3: see `docs/parsers/uniswap_v3.md`

## Multiprocessing

For million-scale workloads, shard `positions` across processes. Create one
`DexamineSession` per worker process.
