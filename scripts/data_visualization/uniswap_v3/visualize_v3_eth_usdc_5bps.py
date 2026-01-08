# Import packages
import sys
import os
import logging
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../"))

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v3 import parse_uni_v3_events

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = "scripts/data_visualization/uniswap_v3/eth_usdc.log"
logging.basicConfig(
    filename=PATH_LOGS + log_name,
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    filemode="w+",
)
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

###################################################################################################
# Changeable variables: Blocks and output file.
###################################################################################################
# Import test data
# file_in = '/media/m2_front/research/data/projects/quantum_defi/0_raw/usdc_eth_5bps_october_2023_test.csv'

# Full data set
file_in = "/media/m2_front/research/data/projects/defi_price_impact/0_raw/usdc_eth_5bps_2023-11-23.csv"

###################################################################################################
# Load CSV file
###################################################################################################
na_values_list = [
    "NA",
    "#N/A",
    "N/A",
    "n/a",
    "NA",
    "#NA",
    "NULL",
    "null",
    "NaN",
    "-1.#IND",
    "",
]
df = pd.read_csv(file_in, na_values=na_values_list)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

pprint(df)
pprint(df.columns)
# pprint(df[df.columns[19]])

###################################################################################################
# Plotting the 'price' column
###################################################################################################
plt.figure(figsize=(10, 6))
plt.plot(df["timestamp"], df["price"], label="Price")
plt.title("Price Over Time")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.savefig("figures/price_plot.png")

###################################################################################################
# Plotting the 'price' column
###################################################################################################
plt.figure(figsize=(10, 6))
plt.plot(df["timestamp"], df["amount_0"], label="Dollar Volume")
plt.title("Dollar Volume Over Time")
plt.xlabel("Time")
plt.ylabel("Dollar Volume")
plt.legend()
plt.savefig("figures/dollar_volume_plot.png")

###################################################################################################
# Providing summary statistics
###################################################################################################
summary_statistics = df["amount_0"].describe()
print("Summary Statistics for USDC:")
print(summary_statistics)

mev = df[df["to_type"] == "mev"]
pprint(mev.count())
