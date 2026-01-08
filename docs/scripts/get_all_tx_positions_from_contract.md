# Get all tx positions form contract

#### Main Script - `main.sh`
`main.sh` is the primary script that orchestrates the overall data extraction and
processing workflow.

```bash
poetry run ./main.sh [optional: path to custom config file]
```
If a custom config file path is not provided, default_config.cfg is used.

#### Configuration File - `default_config.cfg`
Contains configuration settings used by `main.sh` for specifying contract addresses and file paths.

Contents:
- `CONTRACT_ADDRESS`: Address of the Ethereum contract to query.
- `OUTPUT_FILE_CSV`: Path for the output CSV file from `query_contract.sh`.
- `OUTPUT_FILE_JSON`: Path for the output JSON file from `csv_to_json.py`.

#### Bash script - `query_contract.sh`
Executes a TrueBlocks query to extract transaction data for a specified Ethereum contract.

```bash
./query_contract.sh <contract_address> <output_file.csv>
```
- `<contract_address>`: Ethereum contract address to query.
- `<output_file.csv>`: Path to save the output CSV file.

#### Python Script - `csv_to_json.py`
Transforms the CSV file of transaction data from chifra into a JSON format. The reason this is
important is that chifra can output duplicates.

```bash
python csv_to_json.py <input_path.csv> <output_path.json>
```
