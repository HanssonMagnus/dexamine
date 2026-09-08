# Working with the output

`dexamine` returns plain Python objects and writes nothing to disk. This page shows the
common ways to get from parsed events to a file or a dataframe. None of these libraries
is a dependency of `dexamine`; install whichever you already use.

## Straight to CSV

`output_format="flat"` yields one dictionary per event with a stable key order, which
maps directly onto `csv.DictWriter` — no extra dependency:

```python
import csv

from dexamine import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")
rows = session.parse_positions(
    positions=[(12376729, 59), (12376729, 60)],
    protocol="uniswap_v3",
    exchange_pair_address=None,
    batch_size=2000,
    output_format="flat",
)

with open("uniswap_v3_events.csv", "w", newline="", encoding="utf-8") as file:
    writer = None
    for row in rows:
        if writer is None:
            writer = csv.DictWriter(file, fieldnames=list(row))
            writer.writeheader()
        writer.writerow(row)
```

`parse_positions` is a generator, so this streams: memory use stays flat regardless of
how many positions you pass.

The column order is fixed and documented, and is also available programmatically:

```python
from dexamine.api.flat_output import (
    FLAT_UNISWAP_V2_COLUMNS,
    FLAT_UNISWAP_V3_COLUMNS,
)
```

## Into a dataframe

For an amount of data that fits in memory:

```python
import pandas as pd

frame = pd.DataFrame(rows)          # rows from parse_positions(..., output_format="flat")
```

or, with [Polars](https://pola.rs):

```python
import polars as pl

frame = pl.DataFrame(list(rows))
```

## Into Parquet

Parquet is a good archival format for parsed events: columnar, compressed, and typed.

```python
import polars as pl

pl.DataFrame(list(rows)).write_parquet("uniswap_v3_events.parquet")
```

For volumes too large to materialize, write in batches with
[`pyarrow.parquet.ParquetWriter`](https://arrow.apache.org/docs/python/parquet.html), or
write CSV as above and convert afterwards.

Parquet files cannot be read in a text editor. To inspect one from the command line:

```bash
pip install parquet-cli
parq uniswap_v3_events.parquet --head 10
```

## Scaling out

A `DexamineSession` caches ABIs and pool and token metadata, so create **one per
process** and reuse it. To use more than one core, shard the positions across worker
processes and build a session inside each worker:

```python
import multiprocessing as mp

from dexamine import DexamineSession


def parse_shard(positions):
    session = DexamineSession.from_node_url("http://localhost:8545")
    return list(
        session.parse_positions(
            positions=positions,
            protocol="uniswap_v3",
            exchange_pair_address=None,
            batch_size=2000,
            output_format="flat",
        )
    )


if __name__ == "__main__":
    shards = [all_positions[i::8] for i in range(8)]
    with mp.Pool(8) as pool:
        for shard_rows in pool.imap_unordered(parse_shard, shards):
            ...   # write each shard to its own file, then concatenate
```

Every flat row carries `block_number`, `tx_index` and `receipt_log_index`, so rows stay
uniquely addressable and can be re-sorted into chain order after the shards are merged.
