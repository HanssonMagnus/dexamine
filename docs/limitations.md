# Scope and limitations

`dexamine` deliberately does one thing: turn a transaction position into the Uniswap
events that transaction emitted, joined with its execution metadata. This page states
the boundary precisely, and documents the parsing behaviours worth understanding before
relying on the output.

## In scope

- **Chain**: Ethereum mainnet.
- **Protocols**: Uniswap v2 and Uniswap v3.
- **Events**: `swap`, `mint` and `burn`.
- **Data source**: transaction receipt logs, read over JSON-RPC.
- **Input**: a `(block_number, tx_index)` position.
- **Output**: nested payloads plus parsed events (`raw`), or one flat row per event
  (`flat`).

## Out of scope

- **Uniswap v4.** Not supported, and not planned. v2 and v3 give every pool its own
  contract, so an event's pool is its emitting address. v4 routes all pools through a
  single `PoolManager`, identifying them by a `PoolId` in the event data, and adds hooks
  and flash accounting. That is a different parser and a different metadata model, not
  an extension of this one. See [Uniswap v4 transactions](#uniswap-v4-transactions)
  below for what `dexamine` does when it meets one.
- **Other decentralized exchanges and other chains.** Adding them would mean a second
  set of event signatures, decoding rules and pool-state conventions per protocol. A
  narrow, well-tested parser is more useful than a broad, shallow one.
- **The mempool and raw calldata.** `dexamine` reads receipt logs, so it sees only what
  actually executed. Failed transactions emit no Uniswap events and therefore produce no
  rows. Intent expressed in calldata but not realised on-chain is not visible.
- **Discovering which transactions to parse.** That is an indexing problem;
  [TrueBlocks](https://github.com/TrueBlocks/trueblocks-core) and similar tools solve it,
  and `dexamine` consumes the positions they produce.
- **Storage, analysis and plotting.** The package returns Python dictionaries. Write
  them to CSV, Parquet, a database or a dataframe with whatever you already use.
- **Curated third-party label data.** Lists of MEV bots, aggregator registries and the
  like decay and disagree with one another, which would make the package's output depend
  on when it was run. See [Transaction routing](#transaction-routing) below.

## Parsing behaviours to know

### Uniswap v2 requires a preceding `Sync` event

Uniswap v2 publishes post-event reserves in a `Sync` log emitted immediately before each
`swap`, `mint` or `burn` from the same pool. `dexamine` verifies that ordering, and
**skips** any event for which it does not hold, logging an error, rather than reporting
a pool state it cannot substantiate. In practice this ordering always holds for pools
that follow the reference implementation.

### Fee-on-transfer and rebasing tokens

For Uniswap v2 swaps, net amounts are computed as `amount0In - amount0Out` and
`amount1In - amount1Out`. For ordinary token pairs exactly one leg of each pair is
non-zero, so this is exact. Tokens that move balances during a transfer — reflection or
fee-on-transfer designs — can make both legs non-zero, in which case the net amount
reflects the token's own mechanics as well as the trade. Understand the ERC-20 you are
analysing. See
[`parsers/uniswap_v2.md`](./parsers/uniswap_v2.md#notes-on-uniswap-v2-swaps-net-amounts).

### Uniswap v4 transactions

A transaction that swaps through Uniswap v4 produces **no rows**, because the v2 and v3
parsers match on those protocols' event signatures and v4's `PoolManager` emits its own.
The transaction is not rejected, and no error is raised; the result simply contains no
events.

This interacts with the routing classification in a way worth understanding. The
universal router that serves v4
(`0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af`) is a canonical Uniswap deployment, so it
is in `constants.uniswap_address_list` and `parse_to_type` classifies it as
`uniswap_router` — correctly, since `tx_to_type` describes the transaction's destination
address, not the pools it touched. But because a v4 transaction produces no events, no
row is emitted to carry that label. What you observe is simply an empty result.

The practical consequence: **an empty result is not evidence that a transaction did no
Uniswap trading.** If you are counting Uniswap activity over recent blocks, transactions
that route to v4 will be silently absent. Check the destination address yourself if that
distinction matters to your analysis.

### Uniswap v3 virtual reserves at zero liquidity

A v3 `swap` event reports the pool's liquidity after the swap, which can legitimately be
`0` at a tick boundary. Virtual reserves are not meaningful in that case, so `dexamine`
reports `event_virtual_reserve_0` and `event_virtual_reserve_1` as `None` rather than
`0`. The rest of the row — amounts, tick, price — is unaffected.

### Missing values are `None`, never `0`

Throughout the flat schema, a field that does not apply or is absent from the node
response is `None`. A legacy transaction has `tx_max_fee_per_gas = None`; a `mint` row
has `event_price = None`. Zero always means the value was genuinely zero.

### Transaction routing

`tx_to_type` classifies how a transaction reached the pool, using one input: the
transaction's `to` address, matched against the canonical Uniswap deployments in
`dexamine/shared/constants.py:uniswap_address_list`. It takes three values:
`uniswap_router`, `other_contract` and `contract_creation`.

This is deliberately coarse. Finer attribution — labelling arbitrage or other
maximal-extractable-value activity, for instance — would require a curated list of
addresses, and such lists decay: software embedding one silently changes its output as
the list ages, so results published with one version cannot be reproduced with another.
`other_contract` is the natural starting point for users who want to apply their own
labelling, which they can then state and version alongside their analysis.

## Determinism and reproducibility

For a given position and a given chain history, `dexamine` produces the same output every
time. Two things are read at the *latest* block rather than historically: token symbols
and decimals, and a pool's token pair. These are immutable for standard ERC-20 tokens and
Uniswap pools, so in practice the output is stable — but a token with an upgradeable
`symbol()` is a theoretical exception.

`dexamine` derives everything else from the chain itself, so an analysis can be
regenerated from a node rather than from a snapshot of a third party's database.
