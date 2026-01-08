# Import packages
from dataclasses import dataclass, field, asdict
from typing import Optional
from pprint import pprint


# Import modules
from dexamine.shared.general_classes import DexEvent


########################################################################################
# Define a base event class for Uniswap v2 events
########################################################################################
@dataclass
class UniswapV2Event(DexEvent):
    """
    Data Class for the Uniswap v2 events: Swap, mint, and burn and including the sync
    event after the swap/mint/burn event itself. This ensures that the parsing functions
    collect the same information for all event types.
    """

    event_type: str  # "swap", "mint", or "burn".
    reserve_0: int  # Inventory of token 0 in the liquidity pool after the event.
    reserve_1: int  # Inventory of token 1 in the liquidity pool after the event.
    amount_0_in: Optional[int] = None  # Token 0 into pool (only in swap events).
    amount_0_out: Optional[int] = None  # Token 0 out of pool (only in swap events).
    amount_1_in: Optional[int] = None  # Token 1 into pool (only in swap events).
    amount_1_out: Optional[int] = None  # Token 1 out of pool (only in swap events).
    amount_0: Optional[int] = None  # Net flow of token 0 from the liquidity pool.
    amount_1: Optional[int] = None  # Net flow of token 1 from the liquidity pool.
    mid_price: float = field(init=False)  # Mid-price after the event
    invariant: float = field(init=False)  # Invariant after the event

    def __post_init__(self):
        # Validations
        if self.event_type not in ["swap", "mint", "burn"]:
            raise ValueError(
                "event_type must be one of 'swap', 'mint', or 'burn', "
                f"got '{self.event_type}'."
            )

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

        # For Lp events
        if self.event_type in ["mint", "burn"]:
            # Validations
            if self.amount_0 is None or self.amount_1 is None:
                raise ValueError(
                    "For LP events, both amount_0 and amount_1 must be provided."
                )

            if (self.amount_0 * self.amount_1) < 0:
                raise ValueError(
                    "For LP events, amount_0 and amount_1 must be of the same sign."
                )

            # Transform LP amounts to base units
            self.amount_0 = self.transform_to_base(self.amount_0, self.decimals_0)
            self.amount_1 = self.transform_to_base(self.amount_1, self.decimals_1)

        # For Swap event
        elif self.event_type == "swap":
            # Ensure all swap amounts are provided
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

            self.amount_0_in = self.transform_to_base(self.amount_0_in, self.decimals_0)
            self.amount_0_out = self.transform_to_base(
                self.amount_0_out, self.decimals_0
            )
            self.amount_1_in = self.transform_to_base(self.amount_1_in, self.decimals_1)
            self.amount_1_out = self.transform_to_base(
                self.amount_1_out, self.decimals_1
            )
            self.amount_0 = self.amount_0_in - self.amount_0_out
            self.amount_1 = self.amount_1_in - self.amount_1_out

    # Class methods
    def calculate_mid_price(self) -> float:
        """Calculates mid-price after the event."""
        return self.reserve_0 / self.reserve_1 if self.reserve_1 != 0 else 0

    def calculate_invariant(self) -> float:
        """Calculates product of reserves (invariant) after the event."""
        return self.reserve_0 * self.reserve_1


swap_event = UniswapV2Event(
    dex_symbol="UniswapV2",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    event_type="swap",
    reserve_0=150000000000000000000000,
    reserve_1=100000000000000000000,
    amount_0_in=1000000000,
    amount_0_out=0,
    amount_1_in=0,
    amount_1_out=50000000000000000000,
)

lp_event = UniswapV2Event(
    dex_symbol="UniswapV2",
    symbol_0="ETH",
    symbol_1="DAI",
    decimals_0=18,
    decimals_1=18,
    event_type="mint",
    reserve_0=1000000,
    reserve_1=2000000,
    amount_0=500,
    amount_1=500,
)

pprint(asdict(swap_event))
pprint(type(swap_event))
pprint(asdict(lp_event))
