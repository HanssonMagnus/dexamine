# dexamine 🦐
Navigate the currents of DEX data with `dexamine` -- your agile guide through the
digital depths.

`dexamine` is a Python package to examine decentralize exchange (DEX) data. Built on top
of an Ethereum archive node, it provides a robust toolset for transforming complex DEX
transactions into structured datasets for research and data science.

This repository focuses on **Uniswap v2/v3 parsing from transaction receipt logs**.

*Data divers and blockchain biologists, ready your nets -- a new exploration awaits!*

### Project Information
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://python.org)
[![pytest and pylint](https://github.com/HanssonMagnus/dexamine/actions/workflows/pytest-and-pylint.yml/badge.svg)](https://github.com/HanssonMagnus/dexamine/actions/workflows/pytest-and-pylint.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

## Release Notes

### v0.1.0
- Initial version with support for Uniswap v2, Uniswap v3, and Sushiswap.

## Parser Overview and Pipeline
<table>
<tr><th>Constant Product Markets</th><th>Liquidity Aggregators</th><th>Other AMMs</th></tr>
<tr><td>

| Protocol | Status |
|------------|--------|
| Uniswap v2 | ✅ |
| Uniswap v3 | ✅ |
| Sushiswap | 🕒 |
| PancakeSwap | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| 1Inch | ❌ |
| CoW Swap | ❌ |
| Matcha | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| Balancer | ❌ |
| Curve | ❌ |

</td></tr>
</table>


✅: Included. 🕒: Under development. ❌: Not prioritized at the moment.

## Repository Structure
- [`dexamine/`](./dexamine/): Python package source code.
    - [`./parsers/`](./dexamine/parsers/): DEX parsers.
    - [`./resources/`](./dexamine/resources/): Shared resources such as ABIs.
    - [`./shared/`](./dexamine/shared/): Shared utilities and common code.
    - [`./tests/`](./dexamine/tests/): Tests.
- [`docs/`](./docs/): Comprehensive documentation of `dexamine`.
- [`paper/`](./paper/): Accompanying paper.

## Setup
- Create a local virtual environment:
  - `python3 -m venv .venv`
- Activate it:
  - `source .venv/bin/activate`
- Upgrade pip and install:
  - `python -m pip install --upgrade pip`
  - `python -m pip install -e ".[dev]"`

## Development
- Install pre-commit hooks:
  - `pre-commit install`
- Run the same checks as CI:
  - `pre-commit run --all-files`

## Usage
Refer to individual READMEs in [`docs/`](./docs/) for detailed usage instructions for each script
and parser.

## FAQ

#### Are there any user tutorials for `dexamine`?
See the package documentation.

#### Are there datasets parsed with `dexamine` available?
If you want to use data that are parsed with `dexamine` without using the package
yourself, you can find some uploaded datasets at
[Kaggle](https://www.kaggle.com/magnushansson/datasets).

#### How can I cite `dexamine`?
If you use this package or data parsed with this package in a paper or report please
cite it. The citation details can be found in the [`CITATION.cff`](./CITATION.cff) file
in this repository.

#### How can I contribute?
All contributions to the project are welcome, such as code, documentation, bug reports, and
research applications. Please refer to [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines.

#### What license does `dexamine` have?
This project is licensed under GNU General Public License version 3 (GPL-3.0). GPL-3.0 is a free,
copyleft license provided by the Free Software Foundation, designed to ensure software freedom. It
allows users to run, share, modify, and study the software, while requiring that all distributed
copies, modified or not, be available under the same license.

See the [`LICENCE`](./LICENSE) file for more details.

#### How can I show my support?
Leave a ⭐️ if this project helped you!

#### What is up with the shrimp 🦐?
The name `dexamine` (dex + examine) is also inspired by Dexamine, a genus of small
crustaceans in the family Dexaminidae. These creatures are notable for their
drag-powered swimming technique, allowing them to move effectively through their aquatic
environments. Similarly, `dexamine` is designed to efficiently sift through the vast and
complex data of decentralized exchanges.

## Known research papers that use `dexamine`
- [Hansson, Price Discovery in Constant Product Markets, 2023.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4582649)

## Acknowledgements
`dexamine` thanks the teams at
[TrueBlocks](https://github.com/TrueBlocks/trueblocks-core) and
[Erigon](https://github.com/ledgerwatch/erigon) for their support on node operation and
indexing, as well as community members of Flashbots and Unsiwap for their help with
understanding the DeFi protocols.
