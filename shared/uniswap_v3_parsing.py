# Import packages
from web3 import Web3

# Import scirpts
from . import constants


###################################################################################################
# Uniswap v3 general functions
###################################################################################################
def sqrtPriceX96_to_price(sqrtPriceX96, token0_dec, token1_dec):
    '''Convert the sqrtPriceX96 to the regular price and transform it to base units. E.g., for the
    USDC/ETH pair the price will be in dollars per ether, e.g., 2250.'''
    price =(10**token1_dec/10**token0_dec) / (sqrtPriceX96/2**96)**2
    return price

###################################################################################################
# Uniswap v3 ABI call node functions
###################################################################################################
def get_v3_pair(v3_pair_address, uniswap_v3_pair_abi):
    '''Get smart contract addresses for the tokens in a v3 pair from node.'''
    url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(url))
    v3_pair_address = Web3.to_checksum_address(v3_pair_address)
    swap_contract = w3.eth.contract(address=v3_pair_address, abi=uniswap_v3_pair_abi)
    token0 = swap_contract.functions.token0().call()
    token1 = swap_contract.functions.token1().call()
    return token0, token1

def get_v3_dex(v3_pair_address, uniswap_v3_pair_abi):
    '''
    Check if the given pool address belongs to Uniswap V3. Uniswap V3 pools are not ERC20
    contracts, thus there is no way to get the name of the DEX only to validate if it is a known
    DEX.

    Parameters:
    v3_pair_address (str): The address of the pool contract.
    uniswap_v3_pair_abi (str): The ABI of the pool contract.

    Returns:
    str: "UniV3" if the pool belongs to Uniswap V3, "<contract_address>" otherwise.
    '''
    url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(url))
    v3_pair_address = Web3.to_checksum_address(v3_pair_address)
    dex_contract = w3.eth.contract(address=v3_pair_address, abi=uniswap_v3_pair_abi)
    dex_address = dex_contract.functions.factory().call()

    if dex_address == constants.uniswap_v3_factory_address:
        dex_symbol = "UniV3"
    else:
        dex_symbol = dex_address
    return dex_symbol


###################################################################################################
# Uniswp v3 check functions
###################################################################################################
def has_uniswap_v3_swap_event(topics_0):
    '''Check if the tx has any Uniswp v3 swap events.'''
    swap_v3 = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
    if swap_v3 in topics_0:
        return True
    else:
        return False

def has_uniswap_v3_mint_event(topics_0):
    '''Check if the tx has any Uniswp v3 mint events.'''
    mint_v3 = '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde'
    if mint_v3 in topics_0:
        return True
    else:
        return False

def has_uniswap_v3_burn_event(topics_0):
    '''Check if the tx has any Uniswp v3 burn events.'''
    burn_v3 = '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c'
    if burn_v3 in topics_0:
        return True
    else:
        return False
