# Import packages
from web3 import Web3

# Import scirpts
from . import constants

###################################################################################################
# Uniswap v2 ABI call node functions
###################################################################################################
def get_v2_pair(v2_pair_address, uniswap_v2_pair_abi):
    '''Get meta data for an v2 pair from node.'''
    url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(url))
    v2_pair_address = Web3.to_checksum_address(v2_pair_address)
    swap_contract = w3.eth.contract(address=v2_pair_address, abi=uniswap_v2_pair_abi)
    token0 = swap_contract.functions.token0().call()
    token1 = swap_contract.functions.token1().call()
    return token0, token1

def get_v2_dex(v2_pair_address, uniswap_v2_erc20_abi):
    '''Get meta data for an v2 DEX from node.'''
    url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(url))
    v2_pair_address = Web3.to_checksum_address(v2_pair_address)
    dex_contract = w3.eth.contract(address=v2_pair_address, abi=uniswap_v2_erc20_abi)
    dex_symbol = dex_contract.functions.symbol().call()
    return dex_symbol

'''
This function below (get_erc20_symbol) should only be in "general_helpers.py" since it is used for
both v2 and v3 swaps as well as other things. But, if I remove it here I need to also change all
places in the v2 parser where this is called, so I leave it for now, and change it when I have more
time in the future... (hopefully some day)

Now this should be fixed, but I'll keep it here until I have tested it fully.
'''

#def get_erc20_symbol(token_address, uniswap_v2_erc20_abi):
#    '''Match an ERC20 token smart contract address to its symbol.'''
#    # Transform address to checksum address
#    token_address = Web3.to_checksum_address(token_address)
#    try:
#        url = 'http://localhost:8545'
#        w3 = Web3(Web3.HTTPProvider(url))
#        token_address = Web3.to_checksum_address(token_address)
#        token_contract = w3.eth.contract(address=token_address, abi=uniswap_v2_erc20_abi)
#        symbol = token_contract.functions.symbol().call()
#        decimals = token_contract.functions.decimals().call()
#    except Exception as e: # some tokens return symbol as bytes32
#        logger.error(e, exc_info=True)
#        symbol = "unknown"
#
#    return symbol, decimals #string

###################################################################################################
# Uniswp v2 check functions
###################################################################################################
def has_uniswap_v2_swap_event(topics_0):
    '''Check if the tx has a Uniswp v2 swap event.'''
    uniswap_v2_swap_event = constants.uniswap_v2_swap_event
    if uniswap_v2_swap_event in topics_0:
        return True
    else:
        return False

def has_uniswap_v2_burn_event(topics_0):
    '''Check if the tx has a Uniswap v2 burn event for removing liquidity.'''
    uniswap_v2_burn_event = constants.uniswap_v2_burn_event
    if uniswap_v2_burn_event in topics_0:
        return True
    else:
        return False

def has_uniswap_v2_mint_event(topics_0):
    '''Check if the tx has a Uniswap v2 mint event for liquidity provision.'''
    uniswap_v2_mint_event = constants.uniswap_v2_mint_event
    if uniswap_v2_mint_event in topics_0:
        return True
    else:
        return False
