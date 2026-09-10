# Contributing to `dexamine`

Thank you for your interest in contributing. Contributions of all kinds are welcome:
bug reports, documentation improvements, new tests, parser fixes, and research
applications that stretch the package in new directions.

**Before you invest time**: `dexamine` is finished software with a fixed scope, and the
author no longer works in this area. Bug reports and fixes within the documented scope
are welcome and will be looked at, though possibly slowly. Proposals that widen the
scope are likely to be declined — see below. Forking is a perfectly good outcome, and
the license and test suite both support it.

## Getting help and reporting problems

- **Questions and support**: open a
  [GitHub issue](https://github.com/HanssonMagnus/dexamine/issues) with the `question`
  label. There is no separate mailing list or chat; issues are the single channel, so
  that answers stay searchable for the next person.
- **Bug reports**: open an issue and include the `dexamine` version, your Python
  version, the transaction position (`block_number`, `tx_index`) and protocol you were
  parsing, the full traceback, and what you expected instead. A position that reproduces
  the problem is far more useful than a description of it.
- **Feature requests**: open an issue describing the analysis you are trying to do.
  Please read the scope note below first.

Search the existing issues before opening a new one.

## Scope

`dexamine` deliberately does one thing: parse Uniswap v2 and v3 `swap`, `mint` and
`burn` events from Ethereum transaction receipt logs, and return them together with the
transaction's metadata. Contributions that fit that scope are very welcome. Proposals
that would broaden it -- other decentralized exchanges, other chains, mempool or raw
calldata parsing, or bundled analysis and plotting -- are likely to be declined, not
because they are uninteresting, but because a narrow, well-tested parser is more useful
than a broad, shallow one. Open an issue to discuss before writing such code.

This includes **Uniswap v4**: its singleton `PoolManager` architecture needs a different
parser and metadata model, so it belongs in a separate package rather than in this one.

Adding a newly deployed *Uniswap* router address to
`dexamine/shared/constants.py:uniswap_address_list` is in scope and welcome. Adding
curated third-party label data -- lists of MEV bots, aggregator registries, and the like
-- is not: such lists decay, which would make the package's output depend on when it was
run. See the "Transaction routing" section of the paper for the reasoning.

## Development setup

```bash
git clone https://github.com/HanssonMagnus/dexamine.git
cd dexamine
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

## Running the checks

`pre-commit` runs exactly what continuous integration runs:

```bash
pre-commit run --all-files
```

Individually:

```bash
python -m black dexamine        # formatting (line length 88)
python -m pylint --errors-only dexamine
python -m mypy dexamine         # strict mode; must pass with no errors
python -m pytest dexamine/      # offline test suite
```

The default test run is fully offline. To additionally exercise the package against a
real endpoint:

```bash
DEXAMINE_NODE_URL=https://ethereum-rpc.publicnode.com \
    python -m pytest dexamine/ -m integration
```

## Tool versions

The formatter, linter and type checker are pinned to compatible releases in
`pyproject.toml`. This is deliberate: `black` changes its output and `pylint` and `mypy`
add new checks between minor versions, so an unpinned range would make continuous
integration fail on untouched code the day a new release lands. Bump them intentionally,
in a commit of their own, so the resulting reformatting or new warnings are reviewable
separately from the change that prompted them.

## Coding standards

- **Formatting**: `black`, line length 88. Do not hand-format around it.
- **Typing**: every function in `dexamine/` is annotated and `mypy` runs in strict mode.
  New library code must pass without `# type: ignore`, unless a third-party stub makes
  that impossible; if so, use a narrow, error-code-specific ignore and say why.
- **Tests**: new behaviour needs a test, and bug fixes need a test that fails before the
  fix. Unit tests must run offline. Parser tests can use
  `dexamine/tests/helpers.py:make_metadata_resolver` to pre-populate the metadata cache
  so that no node is contacted.
- **Docstrings**: public functions carry a docstring describing arguments, return value,
  and any conditions under which the function returns `None` or raises.
- **Determinism**: the same input position against the same chain history must always
  produce the same output. Anything that would make output depend on wall-clock time or
  on data fetched from a third party needs discussion first.

## Submitting changes

1. Fork the repository and create a branch from `main`.
2. Make your change, with tests.
3. Run `pre-commit run --all-files` and make sure everything passes.
4. Write a commit message that says what changed and why, not just what.
5. Open a pull request against `main` describing the problem and your approach.

## Code of conduct

Participation in this project is governed by the
[Code of Conduct](./CODE_OF_CONDUCT.md).

## License

`dexamine` is licensed under the GNU General Public License v3.0 or later. By
contributing, you agree that your contributions will be licensed under the same terms.
See [`LICENSE`](./LICENSE).
