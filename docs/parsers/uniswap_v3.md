# Parsers Documentation - `node-data` Project

## Uniswap v3

#### parse_uni_v3_events.py
This file contains parsers for liquidity taking and liquidity provision for Uniswap v3.

##### `def parse_v2_trade(logs, swap_index, erc20_abi, uniswap_v3_pair_abi)`:
The swap event in Uniswap v3 is rather straightforward and contain the following variables:

- amount0: pool change in token0 (negative if the pool sends out the amount).
- amount1: pool change in token1 (negative if the pool sends out the amount).
- sqrtPriceX96: mid-price of the pool after the swap expressed in Q notation.
- liquidity: in-range liquidity of pool after the swap.
- tick: tick after the swap was executed.

## Appendix Events
This appendix contains all events emitted by the Uniswap v3 pool contract.

- [IUniswapV3PoolEvents Docs](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents)

- Initialize: Emitted exactly once by a pool when #initialize is first called on the pool.
- Mint: Emitted when liquidity is minted for a given position.
- Collect: Emitted when fees are collected by the owner of a position.
- Burn: Emitted when a position's liquidity is removed.
- Swap: Emitted by the pool for any swaps between token0 and token1.
- Flash: Emitted by the pool for any flashes of token0/token1.
- IncreaseObservationCardinalityNext: Emitted by the pool for increases to the number of
observations that can be stored.
- SetFeeProtocol: Emitted when the protocol fee is changed by the pool.
- CollectProtocol: Emitted when the collected protocol fees are withdrawn by the factory owner.


## Appendix Glorrary
This appendix is based on the following resources:

- [A Primer on Uniswap v3 Math](https://blog.uniswap.org/uniswap-v3-math-primer)
- [A Primer on Uniswap v3 Math Part 2](https://blog.uniswap.org/uniswap-v3-math-primer-2)

#### Liquidity
We can calculate liquidity as the square root of the multiple virtual reserves within the range.
It's stored as a square root for gas efficiency: `L = sqrt(x_virtual * y_virtual)`.

#### Q notation
[Q notation](https://en.wikipedia.org/wiki/Q_(number_format)), commonly referred to as "fixed-point
arithmetic notation," is a way of representing fractional numbers in systems that lack native
support for floating-point numbers. This notation is particularly useful in computing environments
with limited resources, such as embedded systems, where implementing floating-point arithmetic can
be too costly in terms of processing power and memory.

In Ethereum and, more broadly, in the Ethereum Virtual Machine (EVM) that underlies the Ethereum
blockchain, there is no native support for floating-point numbers. This is due to the need for
determinism in a blockchain environment. Floating-point arithmetic can introduce precision issues
and inconsistencies across different computing environments, which is problematic for consensus in
a blockchain.

Uniswap v3 employs Q notation, which can be seen in variables ending with `X96` or `X128`. To
translate a value from Q notation into its real-world equivalent, you divide it by 2 raised to the power of
k, where k represents the count of bits allocated for the fraction part in Q notation. For example,
converting a value like `sqrtPriceX96`, which is in Q96 format, to it `sqrtPrice` involves dividing
it by 2 raised to the power of 96.

#### sqrtPriceX96
In Uniswap v3, the `sqrtPriceX96` value represents the current mid-price in the pool, and it is not
the same as the execution price of a trade. The execution price of a trade in an Automated Market
Maker (AMM) like Uniswap can differ from the mid-price due to price slippage caused by the trade's
size relative to the liquidity.

#### tick
"Ticks" in Uniswap v3 are directly related to the price. It is used to determine the liquidity that
is in range, which results in specific price ranges. Uniswap v3 pools are made up of ticks ranging
from -887272 to 887272, which functionally equate to a token price between 0 and infinity.
Liquidity is constant between two ticks and is treated as an xy=k curve in Uniswap v2 for trading.

You can convert a tick, t, to its mid-price by raising 1.0001 to t. We can calculate the current
price range from the current tick range. If t is the current tick, and ts is the tick-spacing, the
tick-range is [t, t+ts). Which can be directly mapped to a price range by raising 1.0001 to t and
t+ts.

In Uniswap v2, liquidity was represented with ERC-20 LP token and was spread evenly across the
entire xy=k price range. In v3, liquidity providers can concentrate their liquidity, effectively
moving liquidity from the edges of the price range into a price range that a given asset usually
trades within. Uniswap v3 makes LPing much more capital efficient. By concentrating their position
within a price range, LPs can earn more fees on the same amount of capital than in v2. As liquidity
providers shrink their range, the same amount of capital is split among fewer ticks.

For example, for stablecoin pools such as DAI/USDC, LPs can concentrate their capital around the
0.999 to 1.001 range as these two tokens commonly trade within that range. In v2, a $1 million
position would be distributed across the entire xy=k curve and users would only be able to trade
200 USDC for DAI before the price drops down to 0.999.

Alternatively, if the $1 million of liquidity is within the ticks2 that represent the 0.999 to
1.001 range, users would be able to trade 500,000 USDC for DAI before the price moves by the same
amount.

Only swaps can change the tick.

#### tick-spacing
"Tick-spacing" is the distance between two ticks, as defined by the fee tier.

#### Virtual liquidity
In Uniswap v3, when we talk about liquidity in these pools, we really mean virtual liquidity. When
we concentrate liquidity within a range, we construct a virtual xy=k price curve that works exactly
like v2, but within the specified price range. This virtual curve is designed to ensure that the
amount of assets (represented by real x and y) traded as the price approaches either bound of the
range is equal to the real liquidity that has been deposited into the range. Liquidity is constant
between ticks, similar to k in Uniswap v2's xy=k model, and can only be adjusted by depositing or
withdrawing liquidity from the protocol.
