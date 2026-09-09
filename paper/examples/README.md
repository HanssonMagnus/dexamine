# Recorded Uniswap v3 swaps

Install dexamine 1.1.0 using the [installation instructions](../../docs/installation.md),
or install this checkout with `python -m pip install .`. From the repository root:

```bash
python paper/examples/parse_recorded_transaction.py
python paper/examples/parse_recorded_transaction.py --check
python paper/examples/verify_recording.py
```

The script requires the public metadata-seeding API introduced in version 1.1.0.
The example files are a subsequent manuscript revision; download this directory
from the manuscript's linked commit, rather than from the v1.1.0 tag.

## Transaction and interpretation

The example parses transaction **31** (zero-based) in Ethereum mainnet block
**12,561,528**, dated **3 June 2021, 12:21:50 UTC**:
`0xdc9d24ed8c3f62667e2c124f7e8b7b9f2dea1cc668589c36440c504f37421bc2`.
The transaction was selected from previously parsed observations used in the author's
price-impact research. The original project dataset is not required or distributed.

With `protocol="uniswap_v3"` and `exchange_pair_address=None`, the parser returns
all supported v3 events across pools. This receipt contains four v3 swaps, at
zero-based receipt positions **3, 6, 10 and 13**, among 17 logs. Transfers and other
unsupported logs are retained in the raw receipt but do not become output rows.

| Receipt position | Token 0 | Token 1 | Amount 0 | Amount 1 |
| ---: | --- | --- | ---: | ---: |
| 3 | USDC | WETH | -14008.253925 | 5.000000 |
| 6 | DAI | USDC | -13983.724002 | 14008.253925 |
| 10 | DAI | WETH | 13983.724002 | -4.999395 |
| 13 | USDC | WETH | -14003.702900 | 4.999395 |

Amounts above are rounded. Positive quantities enter the emitting pool; negative
quantities leave it. Symbols follow the pool's token0/token1 order. Symbols alone
are not unique identifiers: `data/metadata.json` records token and pool addresses,
and each row's receipt position identifies its emitting address in `data/receipt.json`.

The script explicitly sorts by `receipt_log_index`. That field is an offset within
the transaction receipt, not Ethereum's block-wide `logIndex`. Explicit sorting
also recovers chronological order when the parser groups different event types.
`event_price` measures token 0 per token 1 after each swap; it is not the trade's
average execution price. Virtual reserves describe the local curve at the reported
active liquidity, not total token balances held by the pool.

`expected_output.json` contains every output field for all four swaps, including
price, tick, active liquidity and virtual reserves. Transaction gas used (476,588)
and effective gas price (40 gwei) repeat on each row; they must not be summed across
these rows or interpreted as per-swap costs. The `other_contract` destination label
describes the top-level address match and does not establish an economic purpose.

## Recorded inputs and verification

`data/transaction.json`, `receipt.json` and `block.json` contain unmodified JSON-RPC
response envelopes retrieved from an Erigon 3.3.2 node on 9 September 2026 using
`eth_getTransactionByBlockNumberAndIndex`, `eth_getTransactionReceipt` and
`eth_getBlockByNumber` (transaction hashes only), respectively.
`provenance.json` records the chain, block and transaction identities and capture time.

`metadata_rpc.json` records the requests and responses for `token0()`, `token1()` and
`factory()` for each of the three pools, and `symbol()` and `decimals()` for each of
the three tokens. Every `eth_call` specifies block 12,561,528. `metadata.json` contains
the decoded values; the canonical Uniswap v3 factory identifies the `UniV3` label.
USDC has six decimal places; DAI and WETH have eighteen. This historical metadata
capture is separate from dexamine's normal metadata lookup at the latest block.

Default execution replays the public `JsonRpcClient.call` method and supplies all
recorded metadata through `MetadataResolver.seed`. The session, parser and output
construction run normally, and unexpected HTTP requests fail immediately. The replay
checks RPC parameters before returning responses. It does not import the test suite
or access private resolver state.

`--check` compares the entire output with the committed JSON. `verify_recording.py`
also checks transaction/block identity, decodes the archived metadata calls, and
independently decodes each swap with the web3.py ABI codec. It checks token amounts,
price, tick, active liquidity and virtual reserves using 70-digit decimal arithmetic
and a relative tolerance of 1e-12 for the parser's floating-point output. CI runs both
checks without a node. The raw responses retain the original integers for inspection.

## Optional live retrieval

```bash
python paper/examples/parse_recorded_transaction.py --node-url http://localhost:8545
```

The endpoint must retain the requested transaction, receipt and block. Live mode
uses dexamine's normal metadata resolution at the latest block, so metadata changes
could affect its output; offline mode uses the recorded historical metadata.

## Submission archive

`make -C paper bundle` includes this directory in `recorded-example.zip` alongside
the repository license. After extracting it, install dexamine 1.1.0 with
`python -m pip install git+https://github.com/HanssonMagnus/dexamine.git@v1.1.0`, then run
`python examples/parse_recorded_transaction.py --check` and
`python examples/verify_recording.py` from the extracted directory.
