"""
This file contains the parser for Uniswap v2 events.

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
from dexamine.shared import constants, general_helpers, uniswap_v2_parsing
from dexamine.shared.general_classes import DexEvent, DexEventType

# Get a logger
logger = logging.getLogger(__name__)


########################################################################################
# Define a base event class for Uniswap v2 events
########################################################################################
@dataclass
class UniswapV2Event(DexEvent):
    """
    Data class for Uniswap v2 events that includes the sync event.
    """

    reserve_0: int | float # Inventory of token 0 in the liquidity pool after the event.
    reserve_1: int | float # Inventory of token 1 in the liquidity pool after the event.
    mid_price: float = field(init=False)  # Mid-price after the event.
    invariant: float = field(init=False)  # Invariant after the event.

    def __post_init__(self) -> None:

        # Validate that the reserves are positive
        if self.reserve_0 <= 0:
            raise ValueError(f"reserve_0 must be greater than 0, got {self.reserve_0}")
        if self.reserve_1 <= 0:
            raise ValueError(f"reserve_1 must be greater than 0, got {self.reserve_1}")

        # Transform reserves to base units
        self.reserve_0 = self.transform_to_base(self.reserve_0, self.decimals_0)
        self.reserve_1 = self.transform_to_base(self.reserve_1, self.decimals_1)

        # Calculate mid-price and invariant based on reserves
        self.mid_price = self.calculate_mid_price()
        self.invariant = self.calculate_invariant()

    # Class methods
    def calculate_mid_price(self) -> float:
        """Calculates mid-price after the event."""
        return self.reserve_0 / self.reserve_1 if self.reserve_1 != 0 else 0

    def calculate_invariant(self) -> float:
        """Calculates product of reserves (invariant) after the event."""
        return self.reserve_0 * self.reserve_1


@dataclass
class UniswapV2Swap(UniswapV2Event):
    """
    Data class for Uniswap v2 swap event.
    """

    amount_0_in: int | float # Token 0 into pool (only in swap events).
    amount_0_out: int | float # Token 0 out of pool (only in swap events).
    amount_1_in: int | float # Token 1 into pool (only in swap events).
    amount_1_out: int | float # Token 1 out of pool (only in swap events).
    amount_0: float = field(init=False)  # Net flow of token 0 from liquidity pool
    amount_1: float = field(init=False)  # Net flow of token 1 from liquidity pool
    event_type: str = DexEventType.SWAP.value

    def __post_init__(self) -> None:
        super().__post_init__()  # Call the parent class __post_init__

        # Validate that all swap amounts are provided
        if any(
            v is None
            for v in [
                self.amount_0_in,
                self.amount_0_out,
                self.amount_1_in,
                self.amount_1_out,
            ]
        ):
            raise ValueError(
                "For swap events, all of amount_0_in, amount_0_out, "
                "amount_1_in, and amount_1_out must be provided."
            )

        # Transform amounts to base units
        self.amount_0_in = self.transform_to_base(self.amount_0_in, self.decimals_0)
        self.amount_0_out = self.transform_to_base(self.amount_0_out, self.decimals_0)
        self.amount_1_in = self.transform_to_base(self.amount_1_in, self.decimals_1)
        self.amount_1_out = self.transform_to_base(self.amount_1_out, self.decimals_1)

        # Calculate net amounts
        self.amount_0 = self.amount_0_in - self.amount_0_out
        self.amount_1 = self.amount_1_in - self.amount_1_out

        # Validate that the amounts have different signs
        if not (self.amount_0 * self.amount_1) < 0:
            raise ValueError(
                "For Swap events, amount_0 and amount_1 must have opposite signs."
            )

    # Class methods
    def get_event_data(self) -> dict[str, float | int | str | None]:
        """
        Return the swap object as a dict.

        Return:
            {
            'amount_0': float,
            'amount_0_in': float,
            'amount_0_out': float,
            'amount_1': float,
            'amount_1_in':float,
            'amount_1_out':float,
            'decimals_0': int,
            'decimals_1': int,
            'dex_symbol': 'UniswapV2',
            'event_type': 'swap',
            'invariant': float,
            'mid_price': float,
            'reserve_0': float,
            'reserve_1': float,
            'symbol_0': str,
            'symbol_1': str}

        """
        return asdict(self)


@dataclass
class UniswapV2Lp(UniswapV2Event):
    """
    Data class for Uniswap v2 mint and burn events.
    """

    event_type: str = field(init=False)  # "mint" or "burn"
    amount_0: int | float # Net flow of token 0 from the liquidity pool.
    amount_1: int | float # Net flow of token 1 from the liquidity pool.

    def __post_init__(self) -> None:
        super().__post_init__()  # Call the parent class __post_init__

        # Validate that both amounts are provided
        if self.amount_0 is None or self.amount_1 is None:
            raise ValueError(
                "For LP events, both amount_0 and amount_1 must be provided."
            )

        # Validate that both amounts have the same sign
        if (self.amount_0 * self.amount_1) < 0:
            raise ValueError(
                "For LP events, amount_0 and amount_1 must be of the same sign."
            )

        # Transform LP amounts to base units
        self.amount_0 = self.transform_to_base(self.amount_0, self.decimals_0)
        self.amount_1 = self.transform_to_base(self.amount_1, self.decimals_1)

        # Set event type
        if self.amount_0 > 0:
            self.event_type = DexEventType.MINT.value
        else:
            self.event_type = DexEventType.BURN.value

    # Class methods
    def get_event_data(self) -> dict[str, float | int | str | None]:
        """
        Return the lp object as a dict with all variables of a swap.

        Return:
            {
            'amount_0': float,
            'amount_0_in': None,
            'amount_0_out': None,
            'amount_1': float,
            'amount_1_in':None,
            'amount_1_out':None,
            'decimals_0': int,
            'decimals_1': int,
            'dex_symbol': 'UniswapV2',
            'event_type': 'swap',
            'invariant': float,
            'mid_price': float,
            'reserve_0': float,
            'reserve_1': float,
            'symbol_0': str,
            'symbol_1': str}

        """
        event_data = asdict(self)
        # Add swap-specific amounts as None
        event_data["amount_0_in"] = None
        event_data["amount_0_out"] = None
        event_data["amount_1_in"] = None
        event_data["amount_1_out"] = None
        return event_data


########################################################################################
# Parse all Uniswap v2 swaps, mints, and burns from a transaction
########################################################################################
def parse_all_uniswap_v2_events(
    logs: list[dict[str, Any]],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v2_pair_abi: dict[str, Any],
    exchange_pair_address: str = "",
) -> list[dict[str, float | int | str | None]]:
    """Parse all swaps, mints, and burns from a tx.
    Args:
        logs (dict): Logs from a transaction's receipt.
        erc20_abi (dict): ERC-20 ABI
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi (dict): Uniswap v2 pair ABI
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
        topics_0, [constants.UNISWAP_V2_SWAP_EVENT]
    )
    lp_indexes = general_helpers.get_event_indexes(
        topics_0, [constants.UNISWAP_V2_MINT_EVENT, constants.UNISWAP_V2_BURN_EVENT]
    )

    # Convert exchange_pair_address to checksum
    if exchange_pair_address:
        try:
            exchange_pair_address = Web3.to_checksum_address(exchange_pair_address)
        except ValueError as e:
            logger.error(e, exc_info=True)

    # Parse swaps
    if swap_indexes:  # If the list is not empty
        if exchange_pair_address == "":
            swaps = parse_uniswap_v2_swaps(
                logs, swap_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
            )
            for swap in swaps:
                if swap is not None:  # Since parse_trade(s) can return None
                    events.append(swap)
        else:
            for swap_index in swap_indexes:
                smart_contract = Web3.to_checksum_address(logs[swap_index]["address"])
                if smart_contract == exchange_pair_address:
                    swap = parse_uniswap_v2_swap(
                        logs,
                        swap_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v2_pair_abi,
                    )
                    if swap is not None:
                        events.append(swap)

    # Parse LPs
    if lp_indexes:
        if exchange_pair_address == "":
            lps = parse_uniswap_v2_lps(
                logs, lp_indexes, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
            )
            for lp in lps:
                if lp is not None:
                    events.append(lp)
        else:
            for lp_index in lp_indexes:
                smart_contract = Web3.to_checksum_address(logs[lp_index]["address"])
                if smart_contract == exchange_pair_address:
                    lp = parse_uniswap_v2_lp(
                        logs,
                        lp_index,
                        erc20_abi,
                        erc20_bytes32_abi,
                        uniswap_v2_pair_abi,
                    )
                    if lp is not None:
                        events.append(lp)

    return events


########################################################################################
# Swap parse functions
########################################################################################
def parse_uniswap_v2_swaps(
    logs: list[dict[str, Any]],
    swap_indexes: list[int],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v2_pair_abi: dict[str, Any],
) -> list[dict[str, float | int | str | None] | None]:
    """
    Parse all v2 trades of the tx by identifying all swap events and parse them.

    Args:
        swap_indexes: Index of where the swap event occur in the logs, e.g., [4, 7]
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
    """
    swaps = []
    for swap_index in swap_indexes:
        swap = parse_uniswap_v2_swap(
            logs, swap_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
        )
        swaps.append(swap)

    return swaps


def parse_uniswap_v2_swap(
    logs: list[dict[str, Any]],
    swap_index: int,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v2_pair_abi: dict[str, Any],
) -> dict[str, float | int | str | None] | None:
    """
    Parse a Uniswap v2 swap event.
    Args:
        logs: Logs from receipt of transaction.
        swap_index: An index of where in the logs the swap event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    # Check that the event prior to the swap event is a sync event and that the events
    # have the same address in the logs.
    if not uniswap_v2_parsing.sync_event_is_before_event(logs, swap_index):
        transaction_hash = logs[swap_index]["transactionHash"]
        logger.error(
            "Sync event with same address not before swap event in tx: %s",
            transaction_hash,
            exc_info=True,
        )
        return None

    sync_log = logs[swap_index - 1]  # sync event is just before swap event

    swap_contract = logs[swap_index]["address"]
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(
        swap_contract, uniswap_v2_pair_abi
    )
    dex_symbol = uniswap_v2_parsing.get_v2_dex(swap_contract, erc20_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect the swap amounts delta x_t and delta y_t
    swap_data = logs[swap_index]["data"][2:]  # 256 characters after removing 0x
    amount_0_in = int(swap_data[0:64], 16)  # amount of token0 spent (USDC)
    amount_1_in = int(swap_data[64:128], 16)  # amount of token1 spent (USDC)
    amount_0_out = int(swap_data[128:192], 16)  # amount of token0 received (USDC)
    amount_1_out = int(swap_data[192:256], 16)  # amount of token1 reveived (USDC)

    # Collect NEW exchange rate from the sync event.
    # "Sync: Emitted each time reserves are updated via mint, burn, swap, or sync.
    sync_data = sync_log["data"][2:]  # remove initial 0x
    reserve_0 = int(sync_data[0:64], 16)
    reserve_1 = int(sync_data[64:128], 16)

    # Create swap event object
    swap_event = UniswapV2Swap(
        dex_symbol=dex_symbol,
        symbol_0=symbol_0,
        symbol_1=symbol_1,
        decimals_0=decimals_0,
        decimals_1=decimals_1,
        reserve_0=reserve_0,
        reserve_1=reserve_1,
        amount_0_in=amount_0_in,
        amount_0_out=amount_0_out,
        amount_1_in=amount_1_in,
        amount_1_out=amount_1_out,
    )

    return swap_event.get_event_data()


########################################################################################
# Liquidity provision parse functions
########################################################################################
def parse_uniswap_v2_lps(
    logs: list[dict[str, Any]],
    lp_indexes: list[int],
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v2_pair_abi: dict[str, Any],
) -> list[dict[str, float | int | str | None] | None]:
    """
    Parse all Uniswap v2 LP events (mints and burns) in the transaction logs.

    Args:
        lp_indexes: Index of where the mint and burns event occur in the logs, e.g.,
            [4, 7].
        erc20_abi: ERC-20 ABI.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI.
        uniswap_v2_pair_abi:
    """
    lps = []
    for lp_index in lp_indexes:
        lp = parse_uniswap_v2_lp(
            logs, lp_index, erc20_abi, erc20_bytes32_abi, uniswap_v2_pair_abi
        )
        lps.append(lp)

    return lps


def parse_uniswap_v2_lp(
    logs: list[dict[str, Any]],
    lp_index: int,
    erc20_abi: dict[str, Any],
    erc20_bytes32_abi: dict[str, Any],
    uniswap_v2_pair_abi: dict[str, Any],
) -> dict[str, float | int | str | None] | None:
    """
    Parse a Uniswap v2 lp event (mint or burn).

    Arbs:
        logs: Logs from receipt of transaction.
        mint_index: An index of where in the logs the mint event is.
        erc20_abi: ABI of ERC20 tokens to collect the symbols of the tokens.
        erc20_bytes32_abi (dict): ERC-20 Bytes32 ABI
        uniswap_v2_pair_abi: ABI of the pair to collect the symbol of the DEX.
    """

    # Check that the event prior to the mint event is a sync event and that the events
    # have the same address in the logs.
    if not uniswap_v2_parsing.sync_event_is_before_event(logs, lp_index):
        transaction_hash = logs[lp_index]["transactionHash"]

        logger.error(
            "Sync event with same address not before lp event in tx: %s",
            transaction_hash,
            exc_info=True,
        )
        return None

    sync_log = logs[lp_index - 1]  # sync event is just before lp event

    lp_contract = logs[lp_index]["address"]
    token_0, token_1 = uniswap_v2_parsing.get_v2_pair(lp_contract, uniswap_v2_pair_abi)
    dex_symbol = uniswap_v2_parsing.get_v2_dex(lp_contract, erc20_abi)
    symbol_0, decimals_0 = general_helpers.get_erc20_symbol(
        token_0, erc20_abi, erc20_bytes32_abi
    )
    symbol_1, decimals_1 = general_helpers.get_erc20_symbol(
        token_1, erc20_abi, erc20_bytes32_abi
    )

    # Collect how much was deposited
    lp_data = logs[lp_index]["data"][2:]  # len 128
    amount_0 = int(lp_data[0:64], 16)  # amount of token0 deposited (USDC)
    amount_1 = int(lp_data[64:128], 16)  # amount of token1 deposited (USDC)

    # Change amounts to negative if it's a burn event
    if logs[lp_index]["topics"][0] == constants.UNISWAP_V2_BURN_EVENT:
        amount_0 = -amount_0
        amount_1 = -amount_1

    # Collect NEW exchange rate from the sync event (are the same for LPing).
    # "Sync: Emitted each time reserves are updated via lp, lp, swap, or sync.
    sync_data = sync_log["data"][2:]  # remove initial 0x
    reserve_0 = int(sync_data[0:64], 16)
    reserve_1 = int(sync_data[64:128], 16)

    # Create swap event object
    lp_event = UniswapV2Lp(
        dex_symbol=dex_symbol,
        symbol_0=symbol_0,
        symbol_1=symbol_1,
        decimals_0=decimals_0,
        decimals_1=decimals_1,
        reserve_0=reserve_0,
        reserve_1=reserve_1,
        amount_0=amount_0,
        amount_1=amount_1,
    )

    return lp_event.get_event_data()
