# Parsers Documentation - `dexamine` Project

## Uniswap v2

### Recommended usage (public API)

For Uniswap v2 parsing, prefer the public position-based API (this keeps node access,
batching, and caching consistent):

```python
from dexamine.api.session import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")
result = session.parse_position(
    block_number=10008555,
    tx_index=25,
    protocol="uniswap_v2",
    exchange_pair_address=None,
)
events = result["events"]
```

### Flat output (`output_format="flat"`) for CSV export

For a CSV-friendly output, use `output_format="flat"`. This returns **one row per parsed
event** (so a transaction with multiple events becomes multiple rows).

Important: `output_format="flat"` is **opinionated**. It does not include the full raw
transaction / receipt / block payload. Instead, it emits a selected set of fields
designed for analysis and direct CSV export.

For large workloads, prefer the session generator to stream rows:

```python
from dexamine.api.session import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")
for row in session.parse_positions(
    positions=[(10008555, 25), (10008566, 1)],
    protocol="uniswap_v2",
    exchange_pair_address=None,
    batch_size=2000,
    output_format="flat",
):
    pass
```

Note: `DexamineSession.parse_positions(...)` is a generator. For small experiments you
can materialize it with `rows = list(...)`, but do not do this for large workloads.

Flat columns (Uniswap v2):

```text
timestamp,block_number,index,event_index,hash,from_address,to_address,value,gas,gasPrice,maxPriorityFeePerGas,maxFeePerGas,event_type,dex_symbol,symbol_0,symbol_1,decimals_0,decimals_1,amount_0,amount_1,amount_0_in,amount_0_out,amount_1_in,amount_1_out,reserve_0,reserve_1,mid_price,invariant,to_type
```

For high throughput, use batching:

```python
for parsed in session.parse_positions(
    positions=[(10008555, 25), (10008566, 1)],
    protocol="uniswap_v2",
    exchange_pair_address=None,
    batch_size=2000,
):
    pass
```

### Notes on Uniswap v2 swaps (net amounts)

The parser reports the net traded amounts as:

```text
dxt = amount0In - amount0Out # change in xt (USDC liquidity pool at t)
dyt = amount1In - amount1Out # change in yt (wETH liquidity pool at t)
```

For most currency pairs, if there is an input of token0 the output of token0 is 0 and vice versa.
Therefore, this "net trade" calculation is perfectly fine.

However, this has some implications for certain currency pairs. There are ERC20 tokens that has
built in functionality that is called when you interact with the protocol. For example, the
Safemoon contract returns part of Safemoon tokens to the liquidity pair on the DEX. Therefore, you
can have a swap event that looks like the following,

```text
amount0In = 2081147327526053
amount0Out = 696961612401492081

amount1In = 9776299507275846209
amount1Out = 0
```

Where `Amount0In` is greater than zero. Here the trader inputs `9776299507275846209` but only
receives `696961612401492081` since there is some other latent cost to the specific ERC20 protocol.

To mitigate any potential issues here, I would recommend that you understand the ERC20 protocol
that you are analyzing.

### Sync event ordering

The sync event in the logs outputs the reserves of token0 and token1 in the liquidity pool. The
sync function is called each time a mint, burn, or swap event takes place. However, it is unclear
from the Uniswap v2 docs if the sync event emits the reserves after the mint, burn, or swap has
taken place.

As it turns out after testing, the sync event emits the inventory of the liquidity pool after the swap has taken
place.

### Internal parser module (advanced use)

If you already have receipt logs and want to call the parser directly, see:

- `dexamine/parsers/uniswap_v2_parser.py` (entrypoint: `parse_all_uniswap_v2_events(...)`)
