# `dexamine` documentation

`dexamine` parses Uniswap v2 and v3 `swap`, `mint` and `burn` events from Ethereum
transaction receipt logs, and returns them together with the block, transaction and
receipt metadata of the transaction that emitted them.

## Start here

- [Installation](./installation.md) — install the package and set up a development
  environment.
- [Quickstart](../README.md#quickstart) — parse your first transaction, in the README.
- [Scope and limitations](./limitations.md) — what `dexamine` does, what it does not do,
  and the two parsing behaviours to know before relying on the numbers.

## Reference

- [API](./api.md) — `parse_position`, `DexamineSession`, output formats, and the shared
  `block_*` / `tx_*` / `receipt_*` columns of the flat schema.
- [Uniswap v2 parser](./parsers/uniswap_v2.md) — usage, `event_*` columns, and notes on
  net amounts and `Sync` event ordering.
- [Uniswap v3 parser](./parsers/uniswap_v3.md) — usage, `event_*` columns, the event
  appendix and a glossary (ticks, `sqrtPriceX96`, virtual liquidity).
- [Miscellaneous](./misc/misc_docs.md) — working with the output.

## Project

- [Contributing](../CONTRIBUTING.md) — development setup, checks, coding standards, and
  how to report bugs or ask questions.
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Changelog](../CHANGELOG.md)
- [Paper](https://arxiv.org/abs/2609.10407) — the accompanying preprint,
  arXiv:2609.10407, describing the software architecture, event interpretation, and a
  reproducible example. Its LaTeX source is in [`paper/`](../paper/README.md).
