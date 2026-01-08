# Import modules
from pprint import pprint
from dexamine.shared.general_classes import DexEventType
from dexamine.parsers.uniswap_v3_parser import (
    UniswapV3Swap,
    UniswapV3Mint,
    UniswapV3Burn,
)
from dexamine.parsers import uniswap_v3_parser


########################################################################################
# Define fixtures for the UniswapV3Swap, UnsiwapV3Mint, and UniswapV3Burn instances
########################################################################################
swap_event = UniswapV3Swap(
    dex_symbol="UniV3",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    sender="0xSender",
    recipient="0xRecipient",
    amount_0=2187793161,
    amount_1=-741458298565724583,
    sqrt_price_x96=1458905354048256518860025704567282,
    virtual_liquidity=6718764696431944105,
    tick=196427,
)

pprint(swap_event.get_event_data())
