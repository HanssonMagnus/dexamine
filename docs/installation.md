# Installation

`dexamine` requires **Python 3.10 or newer** and has two runtime dependencies,
[`web3`](https://web3py.readthedocs.io) and
[`requests`](https://requests.readthedocs.io).

## Install the package

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install git+https://github.com/HanssonMagnus/dexamine.git
```

To pin a specific release, append a tag:

```bash
python -m pip install git+https://github.com/HanssonMagnus/dexamine.git@v1.0.0
```

Verify the install:

```bash
python -c "import dexamine; print(dexamine.__all__)"
```

## Development install

```bash
git clone https://github.com/HanssonMagnus/dexamine.git
cd dexamine
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

Run the same checks continuous integration runs:

```bash
pre-commit run --all-files      # black, pylint, mypy (strict), pytest
```

The test suite is offline by default: it replays recorded JSON-RPC responses, so it needs
no node and no network.

## Ethereum endpoint

`dexamine` talks to any Ethereum JSON-RPC endpoint. It uses four methods:
`eth_getTransactionByBlockNumberAndIndex`, `eth_getTransactionReceipt`,
`eth_getBlockByNumber`, and `eth_call` for token and pool metadata.

Because metadata is read at the **latest** block, an archive node — one that retains
historical *state* — is not required. What is required is an endpoint that still serves
the blocks and receipts you want to parse. A pruned endpoint will answer with an error or
a null result for older blocks; `dexamine` surfaces that as a
`JsonRpcResultNotFoundError` or `JsonRpcError` naming the position it could not fetch.

Options, roughly in order of control:

- **Your own node** (for example [Erigon](https://github.com/erigontech/erigon)),
  typically at `http://localhost:8545`. Best for large workloads: no rate limits.
- **A commercial provider.** Fine for moderate volumes. Keep API keys out of source
  control.
- **A public endpoint**, such as `https://ethereum-rpc.publicnode.com`. Good for trying
  the package out. Expect rate limits, and note that some public endpoints are pruned or
  load-balance across pruned backends, so historical blocks may be unavailable
  intermittently.

To exercise the package against a live endpoint:

```bash
DEXAMINE_NODE_URL=https://ethereum-rpc.publicnode.com \
    python -m pytest dexamine/ -m integration
```

These tests skip, with an explanatory message, if the endpoint has pruned the required
history or rate limits the request.
