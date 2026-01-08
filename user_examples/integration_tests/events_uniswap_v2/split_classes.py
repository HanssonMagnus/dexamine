"""
Test dataclasses for Uniswap v2 events.
"""

# Import packages
from dataclasses import dataclass, field, asdict
from pprint import pprint


# Import modules
from dexamine.shared.general_classes import DexEvent, DexEventType


########################################################################################
# Define a base event class for Uniswap v2 events
########################################################################################
@dataclass
class UniswapV2Event(DexEvent):
    """
    Data class for Uniswap v2 events that includes the sync event.
    """

    reserve_0: int  # Inventory of token 0 in the liquidity pool after the event.
    reserve_1: int  # Inventory of token 1 in the liquidity pool after the event.
    mid_price: float = field(init=False)  # Mid-price after the event.
    invariant: float = field(init=False)  # Invariant after the event.

    def __post_init__(self):

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

    amount_0_in: int  # Token 0 into pool (only in swap events).
    amount_0_out: int  # Token 0 out of pool (only in swap events).
    amount_1_in: int  # Token 1 into pool (only in swap events).
    amount_1_out: int  # Token 1 out of pool (only in swap events).
    amount_0: float = field(init=False)  # Net flow of token 0 from liquidity pool
    amount_1: float = field(init=False)  # Net flow of token 1 from liquidity pool
    event_type: str = DexEventType.SWAP.value

    def __post_init__(self):
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
    def get_event_data(self) -> dict:
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
    amount_0: int  # Net flow of token 0 from the liquidity pool.
    amount_1: int  # Net flow of token 1 from the liquidity pool.

    def __post_init__(self):
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
    def get_event_data(self) -> dict:
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


dex_event = DexEvent(
    dex_symbol="UniswapV2",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
)

uniswap_v2_event = UniswapV2Event(
    dex_symbol="UniswapV2",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    reserve_0=150000000000000000000000,
    reserve_1=100000000000000000000,
)


swap_event = UniswapV2Swap(
    dex_symbol="UniswapV2",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    # event_type="swap",
    reserve_0=150000000000000000000000,
    reserve_1=100000000000000000000,
    amount_0_in=1000000000,
    amount_0_out=0,
    amount_1_in=0,
    amount_1_out=50000000000000000000,
)

lp_event = UniswapV2Lp(
    dex_symbol="UniswapV2",
    symbol_0="ETH",
    symbol_1="DAI",
    decimals_0=18,
    decimals_1=18,
    # event_type="mint",
    reserve_0=1000000,
    reserve_1=2000000,
    amount_0=500,
    amount_1=500,
)


pprint(asdict(dex_event))
pprint(type(dex_event))

pprint(asdict(uniswap_v2_event))
pprint(type(uniswap_v2_event))

pprint(asdict(swap_event))
pprint(type(swap_event))

pprint(lp_event.get_event_data())
pprint(type(lp_event))
