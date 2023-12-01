# Import packages
import sys
import os
import logging

# Set the path to the root of the project
sys.path.append(os.path.abspath('../../'))

# Import scirpts
from shared import uniswap_v2_parsing
from shared import general_helpers
from shared import constants

# Get a logger
logger = logging.getLogger(__name__)

###################################################################################################
# Trade parse functions
###################################################################################################
def parse_v2_trades(logs, swap_indexes, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''Parse all v2 trades of the tx by identifying all swap events and parse them.
    Inpur arguments:
        swap_indexes: Index of where the swap event occur in the logs, e.g., [4, 7]
    '''
    trades = []
    for swap_index in swap_indexes:
        try:
            trade = parse_v2_trade(logs, swap_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi)
        except Exception as e:
            logger.error(e, exc_info=True)
        trades.append(trade)

    return trades

def parse_v2_trade(logs, swap_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''
    Parse a Uniswap v2 swap event.
    Input arguments:
        logs: Logs from receipt of transaction.
        swap_index: An index of where in the logs the swap event is.
        uniswap_v2_erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    '''

    # Uniswap v2 sync event
    uniswap_v2_sync_event = constants.uniswap_v2_sync_event

    # Check that the event prior to the swap event is a sync event and that the events have the
    # same address in the logs.
    sync_log = logs[swap_index - 1] # sync event is just before swap event
    if not ((logs[swap_index]['address'] == sync_log['address']) &
        (sync_log['topics'][0] == uniswap_v2_sync_event)):
        logger.error("Sync event not before swap event.", exc_info=True)
        return

    swap_contract = logs[swap_index]['address']
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(swap_contract, uniswap_v2_pair_abi)
    dex_symbol = uniswap_v2_parsing.get_v2_dex(swap_contract, uniswap_v2_erc20_abi)
    symbol_0, decimals_0 = uniswap_v2_parsing.get_erc20_symbol(token_0, uniswap_v2_erc20_abi)
    symbol_1, decimals_1 = uniswap_v2_parsing.get_erc20_symbol(token_1, uniswap_v2_erc20_abi)

    # Collect the swap amounts delta x_t and delta y_t
    swap_data = logs[swap_index]['data'][2:] # 256 characters after removing 0x
    amount0In = int(swap_data[0:64], 16) # amount of token0 spent (USDC)
    amount1In = int(swap_data[64:128], 16) # amount of token1 spent (USDC)
    amount0Out = int(swap_data[128:192], 16) # amount of token0 received (USDC)
    amount1Out = int(swap_data[192:256], 16) # amount of token1 reveived (USDC)

    # Calculate the "net traded amounts"
    dxt = amount0In - amount0Out # change in xt (USDC liquidity pool at t)
    dyt = amount1In - amount1Out # change in yt (wETH liquidity pool at t)
    #dxt = dxt*10**-decimals_0 # transform to "dollars"
    #dyt = dyt*10**-decimals_1 # transform to "dollars"

    # Collect NEW exchange rate from the sync event.
    # "Sync: Emitted each time reserves are updated via mint, burn, swap, or sync.
    sync_data = sync_log['data'][2:] # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    #xt1 = xt1*10**-decimals_0
    yt1 = int(sync_data[64:128], 16)
    #yt1 = yt1*10**-decimals_1
    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    trade = [dex_symbol, symbol_0, symbol_1, decimals_0, decimals_1, dxt, dyt, xt1, yt1, pt1, kt1]

    return trade

###################################################################################################
# Liquidity provision parse functions
###################################################################################################
def parse_v2_mints(logs, mint_indexes, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''Parse all v2 mints of the tx by identifying all mint events and parse them.
    Inpur arguments:
        mint_indexes: Index of where the mint event occur in the logs, e.g., [4, 7]
    '''
    mints = []
    for mint_index in mint_indexes:
        try:
            mint = parse_v2_mint(logs, mint_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi)
        except Exception as e:
            logger.error(e, exc_info=True)
        mints.append(mint)

    return mints

def parse_v2_mint(logs, mint_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''
    Parse a Uniswap v2 mint event (deposit liquidity).
    Input arguments:
        logs: Logs from receipt of transaction.
        mint_index: An index of where in the logs the mint event is.
        uniswap_v2_erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    '''

    # Uniswap v2 sync event
    uniswap_v2_sync_event = constants.uniswap_v2_sync_event

    # Check that event[mint -1] is sync AND
    # Check that sync and mint have same address from logs
    sync_log = logs[mint_index - 1] # sync event is just before mint event
    if not ((logs[mint_index]['address'] == sync_log['address']) &
        (sync_log['topics'][0] == uniswap_v2_sync_event)):
        logger.error("Sync event not before mint event.", exc_info=True)
        return

    mint_contract = logs[mint_index]['address']
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(mint_contract, uniswap_v2_pair_abi)
    dex_symbol = uniswap_v2_parsing.get_v2_dex(mint_contract, uniswap_v2_erc20_abi)
    symbol_0, decimals_0 = uniswap_v2_parsing.get_erc20_symbol(token_0, uniswap_v2_erc20_abi)
    symbol_1, decimals_1 = uniswap_v2_parsing.get_erc20_symbol(token_1, uniswap_v2_erc20_abi)

    # Collect how much was deposited
    mint_data = logs[mint_index]['data'][2:] # len 128
    dxt = int(mint_data[0:64], 16) # amount of token0 deposited (USDC)
    dyt = int(mint_data[64:128], 16) # amount of token1 deposited (USDC)

    # Collect NEW exchange rate from the sync event (are the same for LPing).
    # "Sync: Emitted each time reserves are updated via mint, mint, swap, or sync.
    sync_data = sync_log['data'][2:] # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    yt1 = int(sync_data[64:128], 16)
    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    mint = [dex_symbol, symbol_0, symbol_1, decimals_0, decimals_1, dxt, dyt, xt1, yt1, pt1, kt1]

    return mint

def parse_v2_burns(logs, burn_indexes, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''Parse all v2 burns of the tx by identifying all burn events and parse them.
    Inpur arguments:
        burn_indexes: Index of where the burn event occur in the logs, e.g., [4, 7]
    '''
    burns = []
    for burn_index in burn_indexes:
        try:
            burn = parse_v2_burn(logs, burn_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi)
        except Exception as e:
            logger.error(e, exc_info=True)
        burns.append(burn)

    return burns

def parse_v2_burn(logs, burn_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi):
    '''
    Parse a Uniswap v2 burn event (withdraw liquidity).
    Input arguments:
        logs: Logs from receipt of transaction.
        burn_index: An index of where in the logs the burn event is.
        uniswap_v2_erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    '''

    # Uniswap v2 sync event
    uniswap_v2_sync_event = constants.uniswap_v2_sync_event

    # Check that event[burn -1] is sync AND
    # Check that sync and burn have same address from logs
    sync_log = logs[burn_index - 1] # sync event is just before burn event
    if not ((logs[burn_index]['address'] == sync_log['address']) &
        (sync_log['topics'][0] == uniswap_v2_sync_event)):
        logger.error("Sync event not before burn event.", exc_info=True)
        return

    burn_contract = logs[burn_index]['address']
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(burn_contract, uniswap_v2_pair_abi)
    dex_symbol = uniswap_v2_parsing.get_v2_dex(burn_contract, uniswap_v2_erc20_abi)
    symbol_0, decimals_0 = uniswap_v2_parsing.get_erc20_symbol(token_0, uniswap_v2_erc20_abi)
    symbol_1, decimals_1 = uniswap_v2_parsing.get_erc20_symbol(token_1, uniswap_v2_erc20_abi)

    # Collect how much was burnt
    burn_data = logs[burn_index]['data'][2:] # len 128
    dxt = -int(burn_data[0:64], 16) # amount of token0 withdrawn (USDC)
    dyt = -int(burn_data[64:128], 16) # amount of token1 withdrawn (USDC)

    # Collect NEW exchange rate from the sync event (are the same for LPing).
    # "Sync: Emitted each time reserves are updated via mint, burn, swap, or sync.
    sync_data = sync_log['data'][2:] # remove initial 0x
    xt1 = int(sync_data[0:64], 16)
    yt1 = int(sync_data[64:128], 16)
    pt1 = xt1 / yt1
    kt1 = xt1 * yt1

    burn = [dex_symbol, symbol_0, symbol_1, decimals_0, decimals_1, dxt, dyt, xt1, yt1, pt1, kt1]

    return burn

