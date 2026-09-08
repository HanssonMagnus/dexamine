# Changelog

All notable changes to `dexamine` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-08

### Added

- `MetadataResolver.seed` accepts recorded ERC-20, Uniswap v2 pair, and Uniswap v3
  pool metadata through a public API. It normalizes addresses, copies input mappings,
  and validates addresses before changing the cache. Unseeded lookups still use the
  configured endpoint.
- Metadata value classes are exported from `dexamine.metadata`.

### Changed

- The SoftwareX example seeds metadata through the public API and replays the public
  RPC client interface without importing test helpers or accessing private caches.
- The manuscript includes architecture and destination-label figures, documents
  validation on Python 3.10 through 3.13, and follows the current SoftwareX template.

## [1.0.0] - 2026-09-08

First stable release. The public API and the flat output schema are now considered
stable and will follow semantic versioning.

### Changed

- **Breaking**: the `tx_to_type` routing classification now emits `uniswap_router` and
  `other_contract` instead of `dex_router` and `smart_contract`. `contract_creation` is
  unchanged. The old names were ambiguous: `dexamine` only supports Uniswap, so
  "DEX router" was vague, and both routed cases are smart contracts. See
  [`docs/api.md`](./docs/api.md) for the full definition.
- **Breaking**: the runtime dependencies are now only `web3` and `requests`. `pandas`,
  `polars`, `plotly`, `pyarrow`, `nbformat` and `eth-abi` were declared but imported
  nowhere, and installing `dexamine` no longer pulls them in.
- **Breaking**: the single-call RPC helpers in `dexamine.shared.general_helpers`
  (`get_tx_receipt_block_by_index`, `get_tx_data_by_hash`,
  `get_tx_data_by_block_and_index`, `get_receipt_data_by_hash`,
  `get_block_data_by_block_number`) were removed. `dexamine.rpc.json_rpc_client
  .JsonRpcClient` supersedes them with typed results, batching and explicit exceptions.
- **Breaking**: the unused file loaders `load_txt`, `load_list` and `load_abi` were
  removed from `general_helpers`. Use `get_json_abi` for ABIs.
- The batched path (`DexamineSession.parse_positions`) now raises
  `JsonRpcResultNotFoundError` naming the offending block, transaction index and hash
  when the node answers with a null result, instead of a bare `TypeError` mentioning
  only `NoneType`. This is what a pruned endpoint actually returns.
- `DexamineSession` is now exported from the top-level package:
  `from dexamine import DexamineSession`.
- ABI parameters are typed as `Abi = list[dict[str, Any]]` rather than
  `dict[str, Any]`; ABIs are JSON arrays, so the previous annotation was incorrect.
- `filter_blocks` now returns the filtered mapping in addition to writing it.

### Added

- An opt-in live-node integration suite, gated on the `DEXAMINE_NODE_URL` environment
  variable and the `integration` pytest marker. It skips with an explanatory message
  when the endpoint has pruned the required history or rate limits the request.
- Tests for the log-decoding entrypoints `parse_all_uniswap_v2_events` and
  `parse_all_v3_events`, covering word-level decoding, two's-complement handling, the
  Uniswap v2 `Sync` ordering rule, mint and burn sign conventions, pool-address
  filtering and the Uniswap v3 zero-liquidity boundary case. These paths were previously
  untested.
- `CODE_OF_CONDUCT.md`, a complete `CITATION.cff`, and this changelog.
- Documentation on installation and on the package's scope and limitations.

### Fixed

- `mypy` is configured in strict mode but was never run and did not pass. The library
  now passes strict `mypy`, which runs in pre-commit and in continuous integration.
- Development tooling (`black`, `mypy`, `pylint`, `pytest`, `pre-commit`) is pinned to
  compatible releases. The previous open-ended lower bounds meant a new `black` release
  could fail continuous integration on code nobody had touched.
- Continuous integration now tests Python 3.10 through 3.13, not 3.10 alone.
- Removed the hardcoded personal log path `constants.PATH_LOGS` and the dead
  `PATH_UNISWAP_V*_TEST_DATA_DIR` constants, which pointed at a directory that no longer
  exists.
- Documentation corrections: the routing classification no longer described a
  non-existent MEV category, `docs/misc/misc_docs.md` no longer claimed the package
  outputs Parquet, and the README no longer stated that an archive node is required.

## [0.1.0] - 2026-01-08

Initial release with support for Uniswap v2 and Uniswap v3 on Ethereum mainnet.

### Added

- `parse_position`, `parse_position_raw` and `parse_positions` for parsing by
  transaction position.
- `DexamineSession`, which reuses ABIs and caches pool and token metadata across calls.
- `output_format="flat"`, emitting one CSV-ready row per parsed event.
- A batching JSON-RPC client and a cached metadata resolver.

[1.1.0]: https://github.com/HanssonMagnus/dexamine/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/HanssonMagnus/dexamine/releases/tag/v1.0.0
[0.1.0]: https://github.com/HanssonMagnus/dexamine/releases/tag/v0.1.0
