"""
This file contains the parser for Unsiwap v3 events.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
import logging
from dataclasses import dataclass, field, asdict
from typing import Any
from web3 import Web3

# Import modules
from dexamine.shared import constants, general_helpers, uniswap_v3_parsing
from dexamine.shared.general_classes import DexEvent, DexEventType

# Get a logger
logger = logging.getLogger(__name__)

########################################################################################
# Define dataclasses for Uniswap v3 events
########################################################################################
@dataclass
class UniswapV3Swap(DexEvent):
    """
    Dataclass for Uniswap v3 swap event.
    """

    sender: str  # Address that initiated the swap call, and that received the callback.
    recipient: str  # The address that received the output of the swap.
    amount_0: int | float # The delta of the token0 balance of the pool.
    amount_1: int | float # The delta of the token1 balance of the pool.
    sqrt_price_x96: float  # The sqrt(price) of the pool after the swap, as a Q64.96.
    virtual_liquidity: int  # The virtual liquidity of the pool after the swap.
    tick: int  # The log base 1.0001 of price of the pool after the swap.
    price: float = field(init=False)  # Base unit exchange rate.
    virtual_reserve_0: float = field(init=False)  # Virtual reserev of token 0.
    virtual_reserve_1: float = field(init=False)  # Virtual reserev of token 1.
    event_type: str = DexEventType.SWAP.value  # Type of event.

    def __post_init__(self) -> None:

        # Transform amounts to base units
        self.amount_0 = self.transform_to_base(self.amount_0, self.decimals_0)
        self.amount_1 = self.transform_to_base(self.amount_1, self.decimals_1)

        # Calculate base unit price
        self.price = self.sqrt_price_x96_to_price()

        # Calculate base unit virtual reserves
        self.virtual_reserve_0 = self.calculate_virtual_reserve_0()
        self.virtual_reserve_1 = self.calculate_virtual_reserve_1()

        # Validate that the virtual reserves are positive
        if self.virtual_reserve_0 <= 0:
            raise ValueError(
                f"virtual_reserve_0 must be greater than 0, got {self.virtual_reserve_0}"
            )
        if self.virtual_reserve_1 <= 0:
            raise ValueError(
                f"virtual_reserve_1 must be greater than 0, got {self.virtual_reserve_1}"
            )

    # Class methods
    def sqrt_price_x96_to_price(self) -> float:
        """Convert the sqrt_price_x96 to the regular price and transform it to base
        units. E.g., for the USDC/ETH pair the price will be in dollars per ether, e.g.,
        2250. The following webpage explains the conversion:
        https://blog.uniswap.org/uniswap-v3-math-primer"""
        sqrt_price = self.sqrt_price_x96 / 2**96
        price = sqrt_price**2
        return (10**self.decimals_1 / 10**self.decimals_0) / price

    def calculate_virtual_reserve_0(self) -> float:
        """Calculate the virtual reserve of token 0 after the swap. Equation 6.5 in
        Uniswap v3 Core Whitepaper."""
        sqrt_price = self.sqrt_price_x96 / 2**96
        virtual_reserve_0 = self.virtual_liquidity / sqrt_price
        return self.transform_to_base(virtual_reserve_0, self.decimals_0)

    def calculate_virtual_reserve_1(self) -> float:
        """Calculate the virtual reserve of token 1 after the swap. Equation 6.6 in
        Uniswap v3 Core Whitepaper."""
        sqrt_price = self.sqrt_price_x96 / 2**96
        virtual_reserve_1 = self.virtual_liquidity * sqrt_price
        return self.transform_to_base(virtual_reserve_1, self.decimals_1)

    def get_event_data(self) -> dict[str, float | int | str | None]:
        """
        Return the swap object as a dict.

        Return:
            {
            'amount': None,
            'amount_0': float,
            'amount_1': float,
            'decimals_0': int,
            'decimals_1': int,
            'event_index': int,
            'dex_symbol': str,
            'event_type': str,
            'owner': None,
            'price': float,
            'recipient': str,
            'sender': str,
            'sqrt_price_x96': int,
            'symbol_0': str,
            'symbol_1': str,
            'tick': int,
            'tick_lower': None,
            'tick_upper': None,
            'virtual_liquidity': int,
            'virtual_reserve_0': float,
            'virtual_reserve_1': float}


        """
        event_data = asdict(self)
        # Add mint/burn-specific data as None
        event_data["amount"] = None
        event_data["tick_lower"] = None
        event_data["tick_upper"] = None
        event_data["owner"] = None
        return event_data


@dataclass
class UniswapV3Mint(DexEvent):
    """
    Dataclass for Uniswap v3 mint event.
    """

    sender: str  # The address that minted the liquidity.
    owner: str  # The owner of the position and recipient of any minted liquidity.
    tick_lower: int  # The lower tick of the position.
    tick_upper: int  # The upper tick of the position.
    amount: int  # The amount of liquidity minted to the position range.
    amount_0: int | float # How much token0 was required for the minted liquidity.
    amount_1: int | float # How much token1 was required for the minted liquidity.
    event_type: str = DexEventType.MINT.value

    def __post_init__(self) -> None:

        # Validate that amount_0 and amount_1 are positive
        if self.amount_0 < 0:
            raise ValueError(f"amount_0 must be greater than 0, got {self.amount_0}")
        if self.amount_1 < 0:
            raise ValueError(f"amount_1 must be greater than 0, got {self.amount_1}")

        # Transform amounts to base units
        self.amount_0 = self.transform_to_base(self.amount_0, self.decimals_0)
        self.amount_1 = self.transform_to_base(self.amount_1, self.decimals_1)

    # Class methods
    def get_event_data(self) -> dict[str, float | int | str | None]:
        """
        Return the lp object as a dict with all variables of a swap.

        Return:
            {
            'amount': int,
            'amount_0': float,
            'amount_1': float,
            'decimals_0': int,
            'decimals_1': int,
            'event_index': int,
            'dex_symbol': str,
            'event_type': str,
            'owner': str,
            'price': None,
            'recipient': None,
            'sender': str,
            'sqrt_price_x96': None,
            'symbol_0': str,
            'symbol_1': str,
            'tick': None,
            'tick_lower': int,
            'tick_upper': int,
            'virtual_liquidity': None,
            'virtual_reserve_0': None,
            'virtual_reserve_1': None}

        """
        event_data = asdict(self)
        # Add swap-specific data as None
        event_data["recipient"] = None
        event_data["sqrt_price_x96"] = None
        event_data["virtual_liquidity"] = None
        event_data["tick"] = None
        event_data["price"] = None
        event_data["virtual_reserve_0"] = None
        event_data["virtual_reserve_1"] = None
        return event_data


@dataclass
class UniswapV3Burn(DexEvent):
    """
    Dataclass for Uniswap v3 burn event.
    """

    owner: str  # The owner of the position for which liquidity is removed.
    tick_lower: int  # The lower tick of the position.
    tick_upper: int  # The upper tick of the position.
    amount: int  # The amount of liquidity to remove.
    amount_0: int | float # The amount of token0 withdrawn.
    amount_1: int | float # The amount of token1 withdrawn.
    event_type: str = DexEventType.BURN.value

    def __post_init__(self) -> None:

        # Validate that amount_0 and amount_1 are negative
        if self.amount_0 > 0:
            raise ValueError(f"amount_0 must be <= 0, got {self.amount_0}")
        if self.amount_1 > 0:
            raise ValueError(f"amount_1 must be <= 0, got {self.amount_1}")

        # Transform amounts to base units
        self.amount_0 = self.transform_to_base(self.amount_0, self.decimals_0)
        self.amount_1 = self.transform_to_base(self.amount_1, self.decimals_1)

    # Class methods
    def get_event_data(self) -> dict[str, float | int | str | None]:
        """
        Return the lp object as a dict with all variables of a swap.

        Return:
            {
            'amount': int,
            'amount_0': float,
            'amount_1': float,
            'decimals_0': int,
            'decimals_1': int,
            'event_index': int,
            'dex_symbol': str,
            'event_type': str,
            'owner': str,
            'price': None,
            'recipient': None,
            'sender': None,
            'sqrt_price_x96': None,
            'symbol_0': str,
            'symbol_1': str,
            'tick': None,
            'tick_lower': int,
            'tick_upper': int,
            'virtual_liquidity': None,
            'virtual_reserve_0': None,
            'virtual_reserve_1': None}

        """
        event_data = asdict(self)
        # Add swap/mint-specific data as None
        event_data["sender"] = None
        event_data["recipient"] = None
        event_data["sqrt_price_x96"] = None
        event_data["virtual_liquidity"] = None
        event_data["tick"] = None
        event_data["price"] = None
        event_data["virtual_reserve_0"] = None
        event_data["virtual_reserve_1"] = None
        return event_data


########################################################################################
# Parse all Uniswap v3 swap, mint, and burn events from a transaction
########################################################################################
def parse_all_v3_events(
    logs: list[dict[str, Any]],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
    exchange_pair_address: str = "",
) -> list[dict[str, float | int | str | None]]:
    """
    Parse all Unsiwap v3 swaps, mints, and burns from a tx.

    Args:
        logs (dict): Logs from a transaction's receipt.
        erc20_abi (dict): ERC-20 ABI
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v3_pair_abi (dict): Uniswap v3 pair ABI
        exchange_pair_address (str): Exchange pair smart contract address that you want
        to match

    Returns:
        list: Containing lists of all parsed events
    """
    events = []

    # Get the first topic for all events in the logs
    topics_0 = general_helpers.get_topics_0(logs)

    # Get event hashes
    swap_indexes = general_helpers.get_event_indexes(
        topics_0, [constants.UNISWAP_V3_SWAP_EVENT]
    )
    mint_indexes = general_helpers.get_event_indexes(
        topics_0, [constants.UNISWAP_V3_MINT_EVENT]
    )
    burn_indexes = general_helpers.get_event_indexes(
        topics_0, [constants.UNISWAP_V3_BURN_EVENT]
    )

    # Return the function is no swap, mint, or burn events are found
    if not swap_indexes and not mint_indexes and not burn_indexes:
        return None

    # Convert exchange_pair_address to checksum
    if exchange_pair_address:
        try:
            exchange_pair_address = Web3.to_checksum_address(exchange_pair_address)
        except ValueError as e:
            logger.error(e, exc_info=True)

    # Parse swaps
    if swap_indexes:  # If the list is not empty
        if exchange_pair_address:  # If string is not empty
            for swap_index in swap_indexes:
                smart_contract = Web3.to_checksum_address(logs[swap_index]["address"])
                if smart_contract == exchange_pair_address:
                    swap = parse_v3_swap(
                        logs,
                        swap_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if swap is not None:  # Since parse_swap(s) can return None
                        events.append(swap)

        elif not exchange_pair_address:  # if string is empty, i.e., == ''
            # Parse all swaps regardless of exchange pair
            swaps = parse_v3_swaps(
                logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for swap in swaps:
                if swap is not None:  # Since parse_trade(s) can return None
                    events.append(swap)

    # Parse mints
    if mint_indexes:
        if exchange_pair_address:
            for mint_index in mint_indexes:
                smart_contract = Web3.to_checksum_address(logs[mint_index]["address"])
                if smart_contract == exchange_pair_address:
                    mint = parse_v3_mint(
                        logs,
                        mint_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if mint is not None:
                        events.append(mint)

        elif not exchange_pair_address:
            # Parse all mints regardless of exchange pair
            mints = parse_v3_mints(
                logs, mint_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for mint in mints:
                if mint is not None:
                    events.append(mint)

    # Parse burns
    if burn_indexes:
        if exchange_pair_address:
            for burn_index in burn_indexes:
                smart_contract = Web3.to_checksum_address(logs[burn_index]["address"])
                if smart_contract == exchange_pair_address:
                    burn = parse_v3_burn(
                        logs,
                        burn_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v3_pair_abi,
                    )
                    if burn is not None:
                        events.append(burn)

        elif not exchange_pair_address:
            # Parse all burns regardless of exchange pair
            burns = parse_v3_burns(
                logs, burn_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
            )
            for burn in burns:
                if burn is not None:
                    events.append(burn)

    return events


########################################################################################
# Funtioncs to parse swap events
########################################################################################
# It the parse_v3_swaps function even used???
def parse_v3_swaps(
    logs: list[dict[str, Any]],
    swap_indexes: list[int],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any]
) -> list[dict[str, float | int | str | None] | None]:
    """Parse all v3 swaps of the tx by identifying all swap events and parse them.
    Inpur arguments:
        swap_indexes: Index of where the swap event occur in the logs, e.g., [4, 7]
    """
    swaps = []
    for swap_index in swap_indexes:

        swap = parse_v3_swap(
            logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if swap is not None:
            swaps.append(swap)

    return swaps


def parse_v3_swap(
    logs: list[dict[str, Any]],
    swap_index: int,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
) -> dict[str, float | int | str | None] | None:
    """
    Parse a Uniswap v3 swap event.
    Input arguments:
        logs: Logs from receipt of transaction.
        swap_index: An index of where in the logs the swap event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """
    # Collect meta data
    swap_contract = logs[swap_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        swap_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(swap_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect sender and recipient from topics
    sender = logs[swap_index]["topics"][1]
    recipient = logs[swap_index]["topics"][2]

    # Remove the padding from the eth addresses
    sender = general_helpers.normalize_eth_address(sender)
    recipient = general_helpers.normalize_eth_address(recipient)

    # Collect the swap amounts delta x_t and delta y_t
    swap_data = logs[swap_index]["data"][2:]

    # pool change in token0 and token1(- if pool sends out)
    amount_0 = general_helpers.parse_signed_int(swap_data[0:64])
    amount_1 = general_helpers.parse_signed_int(swap_data[64:128])

    sqrt_price_x96 = int(swap_data[128:192], 16)  # mid-price of the pool after the swap
    virtual_liquidity = int(swap_data[192:256], 16)  # liquidity of pool after the swap
    tick = general_helpers.parse_signed_int(swap_data[256:320])  # tick after the swap

    # Create swap event object
    swap_event = UniswapV3Swap(
        event_index=swap_index,
        dex_symbol=dex_symbol,
        symbol_0=symbol_0,
        symbol_1=symbol_1,
        decimals_0=decimals_0,
        decimals_1=decimals_1,
        sender=sender,
        recipient=recipient,
        amount_0=amount_0,
        amount_1=amount_1,
        sqrt_price_x96=sqrt_price_x96,
        virtual_liquidity=virtual_liquidity,
        tick=tick,
    )

    return swap_event.get_event_data()


########################################################################################
# Functions to parse mint events
########################################################################################
def parse_v3_mints(
    logs: list[dict[str, Any]],
    mint_indexes: list[int],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
) -> list[dict[str, float | int | str | None] | None]:
    """
    Parse all v3 mints of the tx by identifying all mint events and parse them.

    Args:
        mint_indexes: Index of where the mint event occur in the logs, e.g., [4, 7]
    """
    mints = []
    for mint_index in mint_indexes:
        mint = parse_v3_mint(
            logs, mint_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if mint is not None:
            mints.append(mint)

    return mints


def parse_v3_mint(
    logs: list[dict[str, Any]],
    mint_index: int,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
) -> dict[str, float | int | str | None] | None:
    """
    Parse a Uniswap v3 mint event (deposit liquidity).

    Args:
        logs: Logs from receipt of transaction.
        mint_index: An index of where in the logs the mint event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    mint_contract = logs[mint_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        mint_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(mint_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect owner, tick_lower, and tick_upper from topics
    owner = logs[mint_index]["topics"][1]
    owner = general_helpers.normalize_eth_address(owner)  # Remove padding
    tick_lower = general_helpers.parse_signed_int(logs[mint_index]["topics"][2])
    tick_upper = general_helpers.parse_signed_int(logs[mint_index]["topics"][3])

    # Collect how much was deposited
    mint_data = logs[mint_index]["data"][2:]  # len 128
    sender = mint_data[24:64]  # Sender's address
    amount = int(mint_data[64:128], 16)  # Total liquidity amount added
    amount_0 = int(mint_data[128:192], 16)  # Amount of token0 added
    amount_1 = int(mint_data[192:256], 16)  # Amount of token1 added

    # Convert sender to Ethereum address format
    sender = f"0x{sender}"

    # Create mint event object
    mint_event = UniswapV3Mint(
        event_index=mint_index,
        dex_symbol=dex_symbol,
        symbol_0=symbol_0,
        symbol_1=symbol_1,
        decimals_0=decimals_0,
        decimals_1=decimals_1,
        sender=sender,
        owner=owner,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount=amount,
        amount_0=amount_0,
        amount_1=amount_1,
    )

    return mint_event.get_event_data()


########################################################################################
# Functions to parse mint events
########################################################################################
def parse_v3_burns(
    logs: list[dict[str, Any]],
    burn_indexes: list[int],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
) -> list[dict[str, float | int | str | None] | None]:
    """
    Parse all v3 burns of the tx by identifying all burn events and parse them.

    Args:
        logs: Logs from receipt of transaction.
        burn_indexes: Index of where the burn event occur in the logs, e.g., [4, 7]
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """
    burns = []
    for burn_index in burn_indexes:
        burn = parse_v3_burn(
            logs, burn_index, erc20_abi, erc20_bytes32_abi, uniswap_v3_pair_abi
        )

        if burn is not None:
            burns.append(burn)

    return burns


def parse_v3_burn(
    logs: list[dict[str, Any]],
    burn_index: int,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v3_pair_abi: dict[str, Any],
) -> dict[str, float | int | str | None] | None:
    """
    Parse a Uniswap v2 burn event (remove liquidity).

    Args:
        logs: Logs from receipt of transaction.
        burn_index: An index of where in the logs the burn event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI.
        uniswap_v3_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    burn_contract = logs[burn_index]["address"]
    token_0, token_1 = uniswap_v3_parsing.get_v3_pair(
        burn_contract, uniswap_v3_pair_abi
    )
    dex_symbol = uniswap_v3_parsing.get_v3_dex(burn_contract, uniswap_v3_pair_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect owner, tick_lower, and tick_upper from topics
    owner = logs[burn_index]["topics"][1]
    owner = general_helpers.normalize_eth_address(owner)  # Remove padding
    tick_lower = general_helpers.parse_signed_int(logs[burn_index]["topics"][2])
    tick_upper = general_helpers.parse_signed_int(logs[burn_index]["topics"][3])

    # Collect how much was deposited
    burn_data = logs[burn_index]["data"][2:]  # len 128
    amount = int(burn_data[0:64], 16)  # Total liquidity removed

    # Amount of token0 and token1 (set as negative, since out of pool)
    amount_0 = -int(burn_data[64:128], 16)  # Amount of token0 removed
    amount_1 = -int(burn_data[128:192], 16)  # Amount of token1 removed

    # Create mint event object
    burn_event = UniswapV3Burn(
        event_index=burn_index,
        dex_symbol=dex_symbol,
        symbol_0=symbol_0,
        symbol_1=symbol_1,
        decimals_0=decimals_0,
        decimals_1=decimals_1,
        owner=owner,
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount=amount,
        amount_0=amount_0,
        amount_1=amount_1,
    )

    return burn_event.get_event_data()
