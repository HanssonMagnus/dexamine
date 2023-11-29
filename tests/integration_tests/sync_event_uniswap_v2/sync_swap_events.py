# Import packages
import sys
import os
import logging
from pprint import pprint
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Set the precision for Decimal operations
getcontext().prec = 28  # You can adjust this based on the precision you need

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../../'))

# Import scripts
from parsers.uniswap_v2 import parse_uni_v2_events
from shared import general_helpers
from shared import uniswap_v2_parsing
from shared import constants

# Set up logger
path_logs = constants.path_logs
log_name = 'sync_swap_events.log'
logging.basicConfig(filename=path_logs + log_name, level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w+')
logger = logging.getLogger(__name__)
# Example log message
logger.error("Logging setup complete.")

# Import test data
path_uni_v2_by_positions = constants.path_uni_v2_by_positions
data = general_helpers.load_json(path_uni_v2_by_positions)

blocks = list(data.keys())

# Parse transations
#blocks = blocks[83:84] # test with only 1 tx (2 swaps)
#blocks = blocks[0:1] # test with only 1 tx (2 swaps)
total = 0
correct = 0
for block in blocks:
    tx_indexes = data[block]
    for index in tx_indexes:
        # Get transaction data
        try:
            tx = general_helpers.get_tx_data_by_block_and_index(hex(int(block)), hex(int(index)))
            hash = tx['hash']
            #hash = '0x63a1a7ee5fbb6bbe869e18601b67897d4516e53596f0b90b609ee3ae301163ca'
        except Exception as e:
            logger.error(e, exc_info=True)

        # Get receipt data
        try:
            receipt = general_helpers.get_receipt_data_by_hash(hash)
            logs = receipt['logs']
            topics_0 = general_helpers.get_topics_0(logs)
        except Exception as e:
            logger.error(e, exc_info=True)

        if not uniswap_v2_parsing.has_uniswap_v2_swap_event(topics_0):
            logger.error("Does not have Uniswap v2 swap event.", exc_info=True)

        swap_indexes = general_helpers.get_event_index(topics_0, constants.uniswap_v2_swap_event)

        # Load ABIs
        try:
            uniswap_v2_erc20_abi = general_helpers.load_abi(constants.path_uniswap_v2_erc20_abi)
            uniswap_v2_pair_abi = general_helpers.load_abi(constants.path_uniswap_v2_pair_abi)
        except Exception as e:
            logger.error(e, exc_info=True)

        # Parse trade data
        try:
            trades = parse_uni_v2_events.parse_v2_trades(logs, swap_indexes, uniswap_v2_erc20_abi,
                                                        uniswap_v2_pair_abi)
        except Exception as e:
            logger.error(e, exc_info=True)

        for trade in trades:

            symbol_0 = trade[1]
            symbol_1 = trade[2]

            # Check only USDC/WETH since there are many other weird ERC20 contract that have
            # additional transfers built in etc.
            if not (symbol_0=='USDC' and symbol_1=='WETH'):
                continue

            total += 1
            #pprint(symbol_0)
            #pprint(symbol_1)

            decimals_0 = trade[3]
            decimals_1 = trade[4]

            #dxt = trade[5]
            #dyt = trade[6]
            #xt = trade[7]
            #yt = trade[8]

            # Either dxt or dyt is negative.
            dxt = Decimal(trade[5]) # 456056313444833958558829
            dyt = Decimal(trade[6]) # -9776299507275846209
            xt1 = Decimal(trade[7]) # 34380566947687148691700151
            yt1 = Decimal(trade[8]) # 729414612205345013242

            #pprint('---------------------------------------------')
            #pprint(trade[5:9])

            # If I put in 2 into the liquidity pool, I calculate how much I get out by using
            # the value as if I put in 2*(1-0.003) because of the fee.
            fee = Decimal('0.997')
            if dxt > 0: # dxt is deposited to the liquidity pool and we take out dyt
                # Restore liquidity pools to the state before the swap
                # Take the abs here to not mix the positive and negative signs
                xt = xt1 - abs(dxt)
                yt = yt1 + abs(dyt)
                dyt_check = -dxt*fee*yt/(xt+dxt*fee)
                dyt_check_rounded = dyt_check.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                check = [dyt, dyt_check_rounded]

            elif dyt > 0: # dyt is deposited to the liquidity pool and we take out dxt
                xt = xt1 + abs(dxt)
                yt = yt1 - abs(dyt)
                dxt_check = -dyt*fee*xt/(yt+dyt*fee)
                dxt_check_rounded = dxt_check.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                check = [dxt, dxt_check_rounded]

            # For small sums there seems to be some rounding error, and when I adjust for this by
            # just added or subtracting 1, the test pass for 47 out of 48 cases. The one
            # transaction that it does not pass for is a trade of 0.000689 USD.
            if (check[0] == check[1] or check[0] == check[1]+1 or check[0] == check[1]-1):
                correct += 1
            else:
                pprint(hash)
                pprint([dxt, dyt])
                pprint(check)

pprint('Total checked trades: {}'.format(total))
pprint('Total correct trades: {}'.format(correct))
