# Parsers Documentation - `dexamine` Project

## Uniswap v3

### Recommended usage (public API)

For Uniswap v3 parsing, prefer the public position-based API (this keeps node access,
batching, and caching consistent):

```python
from dexamine.api.session import DexamineSession

session = DexamineSession.from_node_url("http://localhost:8545")
result = session.parse_position(
    block_number=12376729,
    tx_index=59,
    protocol="uniswap_v3",
    exchange_pair_address=None,
)
events = result["events"]
```

For high throughput, use batching:

```python
for parsed in session.parse_positions(
    positions=[(12376729, 59), (12376730, 10)],
    protocol="uniswap_v3",
    exchange_pair_address=None,
    batch_size=2000,
):
    pass
```

### Internal parser module (advanced use)

The internal parser lives in `dexamine/parsers/uniswap_v3_parser.py`. If you already have
receipt logs and want to call the parser directly, use:

- `parse_all_v3_events(...)`

#### `parse_all_v3_events(...)`

Parse all Unsiwap v3 swaps, mints, and burns from a tx.

Inputs:

- logs: Logs from transaction receipt.
- exchange_pair_address: string of the exchange pair smart contract address.

For each Uniswap v3 event (swap, mint, burn), the following variables are parsed:

Meta data from the transaction:

- timestamp: The Unix timestamp indicating when the transaction occurred.
- block_number: The number of the block in the Ethereum blockchain in which the
                transaction was recorded.
- index: A sequential number indicating the transaction's position within the block.
- hash: The unique transaction hash, an identifier for the transaction.
- from_address: The Ethereum address of the transaction initiator.
- to_address: The Ethereum address of the transaction recipient.
- value: The amount of Ether transferred in the transaction (is usually 0 for smart
        contract interactions, e.g., Unsiwap).
- gas: The total amount of gas used by the transaction.
- gasPrice: The price of gas (in wei) at the time of the transaction.
- maxPriorityFeePerGas: The maximum priority fee per unit of gas (in wei) specified for
                        the transaction.
- maxFeePerGas: The maximum fee per unit of gas (in wei) the sender is willing to pay.

Variables from the event:

- 'event_type': Specifies the type of event: "swap", "mint", or "burn".
- 'dex_symbol': The symbol of the decentralized exchange.
- 'symbol_0': The symbol of the first token in the exchange pair.
- 'symbol_1': The symbol of the second token in the exchange pair.
- 'decimals_0': The number of decimals of the first token in the exchange pair.
- 'decimals_1': The number of decimals of the second token in the exchange pair.
- 'sender': The address that minted liquidity or swapped.
- 'recipient': The address that received the output of a swap.
- 'owner': The owner of the position and recipient of any minted/burned liquidity.
- 'amount': The amount of liquidity minted/burned to the position range.
- 'amount_0': How much token0 was required for the minted/burned liquidity.
- 'amount_1': How much token0 was required for the minted/burned liquidity.
- 'virtual_liquidity': The virtual liquidity of the pool after the swap.
- 'tick': The log base 1.0001 of price of the pool after the swap.
- 'sqrt_price_x96': The sqrt(mid-price) of the pool after the swap, as a Q64.96.
- 'price': The mid-price of the pool after the swap.
- 'tick_lower': The lower tick of the LP position.
- 'tick_upper': The upper tick of the LP position.
- 'virtual_reserve_0': The virtual reserve of token0 after the swap in base units.
- 'virtual_reserve_1': The virtual reserve of token0 after the swap in base units.
- 'to_type': Type of agent: uni (manual), defi (algorithmic), mev (arbitrage), or
             contract_creation.

#### `parse_v3_swap(...)`

The swap event in Uniswap v3 is rather straightforward and contain the following variables:

- amount0: pool change in token0 (negative if the pool sends out the amount).
- amount1: pool change in token1 (negative if the pool sends out the amount).
- sqrtPriceX96: mid-price of the pool after the swap expressed in Q notation.
- liquidity: in-range liquidity of pool after the swap.
- tick: tick after the swap was executed.

The functions parses out the following variables:

- type_of_event: Specifies the type of event in this case "swap".
- dex_symbol: The symbol of the decentralized exchange, here representing Uniswap v3.
- symbol_0: The symbol of the first token in the trading pair.
- symbol_1: The symbol of the second token in the trading pair.
- decimals_0: The number of decimal places used by the first token.
- decimals_1: The number of decimal places used by the second token.
- amount_0: The amount of the first token in the transaction.
- amount_1: The amount of the second token in the transaction.
- liquidity: The liquidity of the pool after the swap.
- tick: The tick after the swap was executed ('NA' for mints and burns).
- sqrtPriceX96: The square root of the mid-price after the swap in X96 format ('NA' for mints and
  burns).
- price: The transformed mid-price after the swap in base units ('NA' for mints and burns).
- tick_lower: The lower tick of the price range at which to provide liquidity ('NA' for swaps).
- tick_upper: The upper tick of the price range at which to provide liquidity ('NA' for swaps).

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

## Appendix Glossary

This appendix is based on the following resources:

- [A Primer on Uniswap v3 Math](https://blog.uniswap.org/uniswap-v3-math-primer)
- [A Primer on Uniswap v3 Math Part 2](https://blog.uniswap.org/uniswap-v3-math-primer-2)

### Liquidity

We can calculate liquidity as the square root of the multiple virtual reserves within the range.
It's stored as a square root for gas efficiency: `L = sqrt(x_virtual * y_virtual)`.

### Method ID

The method ID is the first 4 bytes of the Keccak-256 hash of the function signature. For example,
to get the method ID for `swapExactInputSingle(...)`, you would hash the full function signature
(including parameter types) and take the first 4 bytes.

### Q notation

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

### sqrtPriceX96

In Uniswap v3, the `sqrtPriceX96` value represents the current mid-price in the pool, and it is not
the same as the execution price of a trade. The execution price of a trade in an Automated Market
Maker (AMM) like Uniswap can differ from the mid-price due to price slippage caused by the trade's
size relative to the liquidity.

### tick

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

### tick-spacing

"Tick-spacing" is the distance between two ticks, as defined by the fee tier.

### Virtual liquidity

In Uniswap v3, when we talk about liquidity in these pools, we really mean virtual liquidity. When
we concentrate liquidity within a range, we construct a virtual xy=k price curve that works exactly
like v2, but within the specified price range. This virtual curve is designed to ensure that the
amount of assets (represented by real x and y) traded as the price approaches either bound of the
range is equal to the real liquidity that has been deposited into the range. Liquidity is constant
between ticks, similar to k in Uniswap v2's xy=k model, and can only be adjusted by depositing or
withdrawing liquidity from the protocol.
