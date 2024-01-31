# ethereum-defi-parser
This project focuses on extracting and analyzing blockchain data from Ethereum archive nodes, with
a specific emphasis on DeFi protocols. It utilizes scripts to query contract data from the Ethereum
blockchain and parsers to process this data into structured datasets for research and data science.

## Release Notes

### v0.1.1
- Add support for Sushiswap.

### v0.0.1
- Initial version with support for Uniswap v2 and v3.

## Pipeline
<table>
<tr><th>Decentralized Exchanges</th><th>Liquidity Aggregators</th></tr>
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

</td></tr> </table>

<table>
<tr><th>Protocols for Loanable Funds</th><th>Yield Aggregators</th></tr>
<tr><td>

| Protocol | Status |
|------------|--------|
| Aave | ❌ |

</td><td>

| Protocol | Status |
|------------|--------|
| Yearn | ❌ |

</td></tr> </table>


✅: Included. 🕒: Under development. ❌: Not prioritized at the moment.


## Repository Structure
- `abis/`: ABIs for the smart contracts used in the project.
- `config/`: Configuration files for scripts.
- `docs/`: Comprehensive documentation for each component.
- `lists/`: Contains text files that are useful for the parsers.
- `parsers/`: Python scripts for parsing blockchain data.
- `scripts/`: Bash scripts for querying blockchain data and Python scripts for creating data sets.
- `shared/`: Shared utilities and common code.
- `test_data/`: Contains test data files and samples.
- `tests/`: Test cases for ensuring code reliability.
    - `tests/unit_tests`: For testing individual functions or classes in isolation.
    - `tests/integration_tests`: For testing the interaction between different modules or components.
    - `tests/end_to_end_tests`: For testing the entire application flow, from start to finish, as a user would experience it.

## Setup
- Activate the virtual environment: `pipenv shell`
- Install dependencies: `pipenv install`

## Usage
Refer to individual READMEs in `docs/` for detailed usage instructions for each script and parser.

## Citation
If you use this package in any research papers or data science reports please cite it. The citation
details can be found in [CITATION.cff](./CITATION.cff) in this repository.

## Contributing
Contributions to the project are welcome. Please refer to `CONTRIBUTING.md` for guidelines.

## License
This project is licensed under [LICENSE NAME]. See `LICENSE` file for details.
