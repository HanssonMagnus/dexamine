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

## Multiprocessing

For million-scale workloads, shard `positions` across processes. Create one
`DexamineSession` per worker process.
