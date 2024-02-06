# ethereum-defi-parser
`ethereum-defi-parser` is a Python package that focuses on extracting and analyzing blockchain data
from Ethereum archive nodes, with a specific emphasis on DeFi protocols. It utilizes scripts to
query contract data from the Ethereum blockchain and parsers to process this data into structured
datasets for research and data science.

### Project Information
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://python.org)
[![Build Status](https://github.com/HanssonMagnus/ethereum-defi-parser/workflows/CI/badge.svg)](https://github.com/HanssonMagnus/ethereum-defi-parser/actions)
[![GitHub issues](https://img.shields.io/github/issues/HanssonMagnus/ethereum-defi-parser.svg)](https://github.com/HanssonMagnus/ethereum-defi-parser/issues)
[![GitHub forks](https://img.shields.io/github/forks/HanssonMagnus/ethereum-defi-parser.svg?style=social&label=Fork)](https://github.com/HanssonMagnus/ethereum-defi-parser)
[![GitHub stars](https://img.shields.io/github/stars/HanssonMagnus/ethereum-defi-parser.svg?style=social&label=Stars)](https://github.com/HanssonMagnus/ethereum-defi-parser)

### Code Quality
[![pylint](https://img.shields.io/badge/just%20the%20message-8A2BE2)](https://github.com/HanssonMagnus/ethereum-defi-parser)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

At this moment in time only Ethereum Mainnet is supported.

## Release Notes

### v0.1.1
- Add support for Sushiswap.

### v0.0.1
- Initial version with support for Uniswap v2 and v3.

## Parser Overview and Pipeline
<table>
<tr><th>Decentralized Exchanges</th><th>Liquidity Aggregators</th><th>Protocols for Loanable Funds</th></tr>
<tr><td>

| Protocol | Status |
|------------|--------|
| Uniswap v2 | ✅ |
| Uniswap v3 | ✅ |
| Sushiswap | 🕒 |
| Curve | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| 1Inch | ❌ |
| CoW Swap | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| Aave | ❌ |
| Compound | ❌ |

</td></tr>
</table>

<table>
<tr><th>Stablecoin Protocols</th><th>Yield Aggregators</th></tr>
</td><td>

| Protocol | Status |
|------------|--------|
| Circle USDC | ❌ |
| Maker DAI | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| Yearn | ❌ |

</td></tr>
</table>


✅: Included. 🕒: Under development. ❌: Not prioritized at the moment.

## Repository Structure
- [`abis/`](./abis/): ABIs for the smart contracts used in the project.
- [`config/`](./config/): Configuration files for scripts.
- [`docs/`](./docs/): Comprehensive documentation for each component.
- [`lists/`](./lists/): Contains text files that are useful for the parsers.
- [`parsers/`](./parsers/): Python scripts for parsing blockchain data.
- [`scripts/`](./scripts/): Bash scripts for querying blockchain data and Python scripts for creating data sets.
- [`shared/`](./shared/): Shared utilities and common code.
- [`test_data/`](./test_data/): Contains test data files and samples.
- [`tests/`](./tests/): Test cases for ensuring code reliability.
    - `tests/unit_tests`: For testing individual functions or classes in isolation.
    - `tests/integration_tests`: For testing the interaction between different modules or components.
    - `tests/end_to_end_tests`: For testing the entire application flow as a user would experience it.

## Setup
- Activate the virtual environment: `pipenv shell`
- Install dependencies: `pipenv install`

## Usage
Refer to individual READMEs in [`docs/`](./docs/) for detailed usage instructions for each script
and parser.

## Citation
If you use this package or data parsed with this package please cite it. The citation details can
be found in the [`CITATION.cff`](./CITATION.cff) file in this repository.

## Contributing
All contributions to the project are welcome, such as code, documentation, bug reports, and
research applications. Please refer to [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines.

## License
This project is licensed under GNU General Public License version 3 (GPL-3.0). GPL-3.0 is a free,
copyleft license provided by the Free Software Foundation, designed to ensure software freedom. It
allows users to run, share, modify, and study the software, while requiring that all distributed
copies, modified or not, be available under the same license.

See the [`LICENCE`](./LICENSE) file for more details.

## Datasets
If you want to use data that are parsed with `ethereum-defi-parser` without using the package
yourself, you can find some uploaded datasets at
[Kaggle](https://www.kaggle.com/magnushansson/datasets).

## Tutorials
See the package documentation.

## Known research papers that use `ethereum-defi-parser`
- [Hansson, Price Discovery in Constant Product Markets, 2023.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4582649)

## Acknowledgements
I want to thank the teams at TrueBlocks and Erigon for their support on node operation, as well as
community members of Flashbots and Unsiwap for their help with understanding the DeFi protocols.

## Showing your support
Leave a ⭐️ if this project helped you!
