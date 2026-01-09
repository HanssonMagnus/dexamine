## API

### Parse a single transaction position

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

### Parse many positions (batched)

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

### Multiprocessing

For million-scale workloads, shard `positions` across processes. Create one
`DexamineSession` per worker process.

