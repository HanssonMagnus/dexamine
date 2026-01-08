"""
This file contains general classes that are shared among the parsers.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

from dataclasses import dataclass, asdict
from enum import Enum


########################################################################################
# DEX classes
########################################################################################
@dataclass
class DexEvent:
    """Class for general DEX events."""

    dex_symbol: str  # Symbol of the DEX.
    symbol_0: str  # Symbol of the first ERC-20 token in the pair (token 0).
    symbol_1: str  # Symbol of the second ERC-20 token in the pair (token 1).
    decimals_0: int  # Number of decimals of token 0.
    decimals_1: int  # Number of decimals of token 1.
    event_index: int # Index of the log event in the transaction. FIX THE REMAINING V2 CODE ALSO!

    @staticmethod
    def transform_to_base(amount: int | float, decimals: int) -> float | int:
        """
        Transforms token amounts to base values based on their decimals. Raise
        ValueError if the amount is None.
        """
        if amount is None:
            raise ValueError("Amount cannot be None for base unit transformation.")
        return amount * 10**-decimals if decimals > 0 else amount

    def get_event_data(self) -> dict[str, float | int | str | None]:
        """Return dataclass object as dict."""
        return asdict(self)


class DexEventType(Enum):
    """Class of predefined DEX event types."""

    SWAP = "swap"  # Uniswap swap event.
    MINT = "mint"  # Uniswap mint event.
    BURN = "burn"  # Uniswap burn event.


########################################################################################
# General classes
########################################################################################
class EthereumToType(Enum):
    """Class of types of Ethereum to addresses."""

    DEX_ROUTER = "dex_router"  # Transaction is sent directly to any DEX router addresses.
    SMART_CONTRACT = "smart_contract"  # Transaction is sent to a DeFi smart contract.
    MEV = "mev"  # Transaction is sent to MEV bot.
    CONTRACT_CREATION = "contract_creation"  # If to_address is empty (None).
