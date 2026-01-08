"""
Test dataclasses for Uniswap v3 events.
"""

# Import packages
from dataclasses import dataclass, field, asdict
from pprint import pprint


# Import modules
from dexamine.shared.general_classes import DexEvent, DexEventType


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


dex_event = DexEvent(
    dex_symbol="UniswapV3",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
)

swap_event = UniswapV3Swap(
    dex_symbol="UniswapV3",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    sender="magnushansson.eth",
    recipient="magnushansson.eth",
    amount_0=-92306344271,
    amount_1=31615983647285313536,
    sqrt_price_x96=1466113147130104396930114109452589,
    virtual_liquidity=6293106105394869801,
    tick=196525,
)

mint_event = UniswapV3Mint(
    dex_symbol="UniswapV3",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    sender="magnushansson.eth",
    owner="magnushansson.eth",
    tick_lower=196525,
    tick_upper=196025,
    amount=100000,
    amount_0=92306344271,
    amount_1=31615983647285313536,
)

burn_event = UniswapV3Burn(
    dex_symbol="UniswapV3",
    symbol_0="USDC",
    symbol_1="WETH",
    decimals_0=6,
    decimals_1=18,
    owner="magnushansson.eth",
    tick_lower=196525,
    tick_upper=196025,
    amount=100000,
    amount_0=92306344271,
    amount_1=31615983647285313536,
)

pprint(dex_event.get_event_data())
pprint(type(dex_event))

pprint(swap_event.get_event_data())
pprint(type(swap_event))

pprint(swap_event.virtual_reserve_0 / swap_event.virtual_reserve_1)

pprint(mint_event.get_event_data())
pprint(type(mint_event))

pprint(burn_event.get_event_data())
pprint(type(burn_event))

pprint(swap_event.get_event_data().keys() == mint_event.get_event_data().keys() == burn_event.get_event_data().keys())
