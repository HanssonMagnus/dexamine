# Recorded Uniswap v3 transaction

From the repository root, with dexamine 1.1.0 installed from the release tag
(or with this checkout installed using `python -m pip install .`):

```bash
python paper/examples/parse_recorded_transaction.py
python paper/examples/parse_recorded_transaction.py --check
```

Before v1.1.0 is tagged, use the permanent commit command in the
[installation instructions](../../docs/installation.md). It includes the required
metadata-seeding API; v1.0.0 does not.

This example parses transaction 59 in Ethereum block 12,376,729, whose hash is
`0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc`.
It created the Uniswap v3 USDC/WETH 0.05% pool and minted its first position.

The default mode reads the existing transaction, receipt and block fixtures in
`dexamine/tests/test_data/node_responses/`. The public `JsonRpcClient.call` method is
replaced with fixture replay;
the public session interface, protocol parser and flat-output construction run normally.
Contract metadata is supplied through the public `MetadataResolver.seed` method: USDC has six
decimals, WETH has eighteen, and the pool contains those tokens in that order.
Unexpected HTTP requests fail immediately. The script checks the requested RPC
parameters against the recorded transaction before returning a response.
No test helper is imported and no private resolver state is accessed. The JSON
fixtures are data inputs; the test suite itself is not needed to run the example.

`expected_output.json` contains the complete result. Its `receipt_log_index` is **5**,
the zero-based offset within the receipt; the source log's block-wide `logIndex` is
**106**. Gas consumption covers the entire transaction, including pool creation.
The example does not allocate that cost to the mint event.

For live retrieval using an endpoint that retains the required history:

```bash
python paper/examples/parse_recorded_transaction.py --node-url http://localhost:8545
```

The output illustrates floating-point rounding: the log stores 2,995,507,735 integer
USDC units, while the normalized quantity may print as `2995.5077349999997`.
The paper rounds that value for display. The original fixture responses remain
unchanged. This example reproduces one parsing result, not the datasets of the
research papers cited in the manuscript.
