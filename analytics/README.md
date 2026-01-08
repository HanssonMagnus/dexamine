# Dexamine Analytics
This directory contains data analysis and validation scripts for examining outputs from
`dexamine`. These scripts provide insights into parsed DEX data, allowing you to verify
data integrity, identify anomalies, and conduct exploratory analysis.

## Directory Structure
- **`uniswap_v3_analysis.py`**: Script for analyzing all parsed trades from a Uniswap V3
pair. This script includes basic checks on returns, volume distributions, and pricing
anomalies to ensure the dataset's accuracy and consistency.

## Usage
To run any script within this directory, ensure that all required dependencies from
`dexamine` are installed and that you have activated the project’s virtual environment.

Example command for executing the Uniswap V3 analytics script:

```bash
python analytics/uniswap_v3_analysis.py
```
