# Import packages
import sys
import os
import logging
from pprint import pprint

# Set the path to the root of the project
sys.path.append(os.path.abspath("../../../../"))

# Import scripts
from parsers.uniswap_v2 import parse_uni_v2_events
from shared import general_helpers
from shared import uniswap_v2_parsing
from shared import constants

# Set up logger
PATH_LOGS = constants.PATH_LOGS
log_name = "tests/parse_v2_mints.log"
logging.basicConfig(
    filename=PATH_LOGS + log_name,
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    filemode="w+",
)
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

# Import test data
PATH_UNISWAP_V2_BY_POSITIONS = constants.PATH_UNISWAP_V2_BY_POSITIONS
data = general_helpers.load_json(PATH_UNISWAP_V2_BY_POSITIONS)

blocks = list(data.keys())

# Parse transations
# blocks = blocks[83:84] # test with only 1 tx (2 swaps)
# blocks = blocks[0:1] # test with only 1 tx (2 swaps)
for block in blocks:
    tx_indexes = data[block]
    for index in tx_indexes:
        # Get transaction data
        try:
            tx = general_helpers.get_tx_data_by_block_and_index(
                hex(int(block)), hex(int(index))
            )
            hash = tx["hash"]
            # pprint(hash)
        except Exception as e:
            logger.error(e, exc_info=True)

        # Get receipt data
        try:
            receipt = general_helpers.get_receipt_data_by_hash(hash)
            logs = receipt["logs"]
            topics_0 = general_helpers.get_topics_0(logs)
        except Exception as e:
            logger.error(e, exc_info=True)

        if not uniswap_v2_parsing.has_UNISWAP_V2_MINT_EVENT(topics_0):
            logger.error("Does not have Uniswap v2 mint event.", exc_info=True)

        mint_indexes = general_helpers.get_event_index(
            topics_0, constants.UNISWAP_V2_MINT_EVENT
        )

        # Load ABIs
        try:
            uniswap_v2_erc20_abi = general_helpers.load_abi(constants.PATH_ERC20_ABI)
            uniswap_v2_pair_abi = general_helpers.load_abi(
                constants.PATH_UNISWAP_V2_PAIR_ABI
            )
        except Exception as e:
            logger.error(e, exc_info=True)

        # Parse all mint events per transaction
        try:
            mints = parse_uni_v2_events.parse_v2_mints(
                logs, mint_indexes, uniswap_v2_erc20_abi, uniswap_v2_pair_abi
            )
        except Exception as e:
            logger.error(e, exc_info=True)

        # Parse individual mint events
        for mint_index in mint_indexes:
            try:
                mint = parse_uni_v2_events.parse_v2_mint(
                    logs, mint_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi
                )
            except Exception as e:
                logger.error(e, exc_info=True)

            if mint == None:
                pprint(hash)
        # for mint in mints:
        # pprint(mint)
