#!/bin/bash
#
########################################################################################
# Uniswap V3
########################################################################################

# Define the path to the main script
MAIN_SCRIPT_V3="/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/main.sh"

# Define an array of config files
CONFIG_FILES=(
    "/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/configs/weth_ens_03.cfg"
    "/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v3/configs/usdc_weth_005.cfg"
    # Add additional config file paths here
)

# Loop through each config file and run the main script with it
for config in "${CONFIG_FILES[@]}"; do
    echo "Running $MAIN_SCRIPT FOR V3 with config $config"
    "$MAIN_SCRIPT_V3" "$config"
done

########################################################################################
# Uniswap V2
########################################################################################

# Define the path to the main script
MAIN_SCRIPT_V2="/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v2/main.sh"

# Define an array of config files
CONFIG_FILES=(
    "/home/magnus/Git/HanssonMagnus/research/dexamine/scripts/complete_event_parsing/uniswap_v2/configs/usdc_weth.cfg"
    # Add additional config file paths here
)

# Loop through each config file and run the main script with it
for config in "${CONFIG_FILES[@]}"; do
    echo "Running $MAIN_SCRIPT FOR V2 with config $config"
    "$MAIN_SCRIPT_V2" "$config"
done
