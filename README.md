# dexamine 🦐

`dexamine` is a Python package that parses Uniswap events from Ethereum transaction
receipt logs. Give it a transaction position — a block number and the index of a
transaction within that block — and it returns the `swap`, `mint` and `burn` events that
transaction emitted, with token symbols and decimals resolved, amounts converted to base
units, and the block, transaction and receipt metadata joined onto every row.

It is built for research: the output is deterministic, derived from the chain rather
than from a hosted dataset, and detailed enough for market-microstructure work — gas
paid, position in block, fee fields, pool state after the event, and how the transaction
was routed to the pool.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-1f425f.svg)](https://python.org)
[![tests](https://github.com/HanssonMagnus/dexamine/actions/workflows/ci.yml/badge.svg)](https://github.com/HanssonMagnus/dexamine/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

## What it supports

| | |
|---|---|
| **Chain** | Ethereum mainnet |
| **Protocols** | Uniswap v2, Uniswap v3 |
| **Events** | `swap`, `mint`, `burn` |
| **Data source** | Transaction receipt logs, via Ethereum JSON-RPC |
| **Output** | Nested Python objects (`raw`) or one flat row per event (`flat`) |

See [Scope and limitations](#scope-and-limitations) for what it deliberately does not do.

## Installation

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install git+https://github.com/HanssonMagnus/dexamine.git
```

For a development install, see [`docs/installation.md`](./docs/installation.md).

## Quickstart

Parse a single transaction by its position in a block. This example is a real Uniswap v2
swap and runs against a public endpoint, so it works without your own node:

```python
from dexamine import parse_position

result = parse_position(
    node_url="https://ethereum-rpc.publicnode.com",
    block_number=10008566,
    tx_index=1,
    protocol="uniswap_v2",
    exchange_pair_address=None,   # or a pool address to parse only that pool
)

for event in result["events"]:
    print(event["event_type"], event["symbol_0"], event["symbol_1"], event["mid_price"])
```

For CSV-ready output, ask for one flat row per event:

```python
import csv
import sys

from dexamine import DexamineSession

session = DexamineSession.from_node_url("https://ethereum-rpc.publicnode.com")

rows = session.parse_positions(
    positions=[(12376729, 59), (12376729, 60)],
    protocol="uniswap_v3",
    exchange_pair_address=None,
    batch_size=2000,
    output_format="flat",
)

writer = None
for row in rows:                       # a generator: stream it, do not materialize it
    if writer is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(row))
        writer.writeheader()
    writer.writerow(row)
```

`DexamineSession` loads ABIs once and caches pool and token metadata, so create one per
process and reuse it. To scale beyond one core, shard the positions across worker
processes and build a session inside each worker.

Full column definitions live in [`docs/api.md`](./docs/api.md),
[`docs/parsers/uniswap_v2.md`](./docs/parsers/uniswap_v2.md) and
[`docs/parsers/uniswap_v3.md`](./docs/parsers/uniswap_v3.md).

## What you need to run it

Any Ethereum JSON-RPC endpoint. `dexamine` reads pool and token metadata at the *latest*
block, so an **archive node is not required**. What is required is an endpoint that still
serves the blocks and receipts you are parsing: a full node with complete history, or a
provider that has not pruned it. Recent blocks work on ordinary public endpoints; the
2020 and 2021 examples above need an endpoint that retains that history.

`dexamine` parses positions; it does not discover them. Finding every transaction that
touched a given pool is an indexing job — [TrueBlocks](https://github.com/TrueBlocks/trueblocks-core)
is one tool for it, and `dexamine` accepts the `(block_number, tx_index)` pairs any
indexer produces.

## Scope and limitations

`dexamine` deliberately does one thing well. It does **not**:

- support decentralized exchanges other than Uniswap, or chains other than Ethereum
  mainnet;
- read the mempool or decode raw transaction calldata — it parses receipt logs, so it
  only ever sees what actually executed;
- discover which transactions to parse (see above);
- bundle analysis, storage or plotting. It returns Python dictionaries; write them
  wherever you like.

Two behaviours are worth knowing before you rely on the numbers:

- **Uniswap v2 requires the `Sync` event.** Post-event reserves are published by the
  `Sync` log that precedes each `swap`, `mint` or `burn` from the same pool. `dexamine`
  verifies this ordering and **skips** events for which it does not hold, rather than
  reporting an unverified pool state.
- **Fee-on-transfer tokens.** For v2 swaps, net amounts are computed as
  `amount0In - amount0Out`. Tokens that move balances during a transfer can make both
  legs non-zero. See the note in
  [`docs/parsers/uniswap_v2.md`](./docs/parsers/uniswap_v2.md).

## Repository structure

- [`dexamine/`](./dexamine/) — package source.
  - [`api/`](./dexamine/api/) — the public API: `parse_position`, `DexamineSession`,
    flat-row construction.
  - [`parsers/`](./dexamine/parsers/) — Uniswap v2 and v3 event decoding.
  - [`rpc/`](./dexamine/rpc/) — the JSON-RPC client, including batching.
  - [`metadata/`](./dexamine/metadata/) — cached pool and ERC-20 metadata resolution.
  - [`shared/`](./dexamine/shared/) — constants, dataclasses and helpers.
  - [`resources/`](./dexamine/resources/) — ABIs.
  - [`tests/`](./dexamine/tests/) — offline unit tests and opt-in integration tests.
- [`docs/`](./docs/docs.md) — documentation.
- [`paper/`](./paper/) — the accompanying software preprint.

## Development

```bash
git clone https://github.com/HanssonMagnus/dexamine.git
cd dexamine
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files      # black, pylint, mypy (strict), pytest
```

The default test run is offline — it replays recorded JSON-RPC responses, so no node is
needed. To also run the live-endpoint tests:

```bash
DEXAMINE_NODE_URL=https://ethereum-rpc.publicnode.com \
    python -m pytest dexamine/ -m integration
```

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for contribution guidelines and
[`CHANGELOG.md`](./CHANGELOG.md) for release history.

## Citing `dexamine`

If you use this package, or data parsed with it, please cite it. Citation metadata is in
[`CITATION.cff`](./CITATION.cff); GitHub renders it as a "Cite this repository" button.
The accompanying paper is in [`paper/paper.tex`](./paper/paper.tex).

## FAQ

#### Are there datasets already parsed with `dexamine`?

Yes — some are published on
[Kaggle](https://www.kaggle.com/magnushansson/datasets) if you would rather not run the
package yourself.

#### How do I report a bug or ask a question?

Open a [GitHub issue](https://github.com/HanssonMagnus/dexamine/issues). Including the
transaction position that reproduces the problem makes it far easier to fix. All
participation is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md).

#### What license does `dexamine` have?

The GNU General Public License v3.0 or later — a free, copyleft license that lets you
run, share, modify and study the software, provided distributed copies stay under the
same terms. See [`LICENSE`](./LICENSE).

#### What is up with the shrimp 🦐?

The name (dex + examine) is also a genus of small crustaceans, *Dexamine*, in the family
Dexaminidae — notable for a drag-powered swimming technique that moves them efficiently
through the water. `dexamine` likewise sifts efficiently through a large volume of
decentralized exchange data.

## Research using `dexamine`

- Hansson, M. (2024). *Price Discovery in Constant Product Markets.*
  [doi:10.2139/ssrn.4582649](https://doi.org/10.2139/ssrn.4582649)

## Acknowledgements

Thanks to the teams at [TrueBlocks](https://github.com/TrueBlocks/trueblocks-core) and
[Erigon](https://github.com/erigontech/erigon) for their support on node operation and
indexing, and to community members of Flashbots and Uniswap for their help in
understanding the protocols.
