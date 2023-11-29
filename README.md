# Node-Data Project

## Overview
This project focuses on extracting and analyzing blockchain data from Ethereum nodes, with a
specific emphasis on DeFi protocols. It utilizes scripts to query data from Ethereum contracts and
parsers to process this data into structured datasets.

## Structure
- `abis/`: ABIs for the smart contracts used in the project.
- `config/`: Configuration files for scripts.
- `docs/`: Comprehensive documentation for each component.
- `lists/`: Contains text files that are useful for the parsers.
- `parsers/`: Python scripts for parsing blockchain data.
- `scripts/`: Bash scripts for querying blockchain data.
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

## Contributing
Contributions to the project are welcome. Please refer to `CONTRIBUTING.md` for guidelines.

## License
This project is licensed under [LICENSE NAME]. See `LICENSE` file for details.
