# Parsers Documentation - `ethereum-defi-parser` Project

## Uniswap v3: parse_uni_v3_events.py
This file contains parsers for liquidity taking and liquidity provision events for Uniswap v3.

##### `parse_all_v3_events(logs, erc20_abi, uniswap_v3_pair_abi, exchange_pair_address='')`
Parse all Unsiwap v3 swaps, mints, and burns from a tx.
Inputs:
logs: Logs from transaction receipt.
exchange_pair_address: string of the exchange pair smart contract address.

##### `parse_v2_trade(logs, swap_index, erc20_abi, uniswap_v3_pair_abi)`
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

## Uniswap v3: parse_uni_v3_raw_tx.py
This file contains parsers for swaps from raw tx data (mempool) for Uniswap v3.

##### `def parse_v3_direct_trades_from_raw_tx(data):`

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

#### Liquidity
We can calculate liquidity as the square root of the multiple virtual reserves within the range.
It's stored as a square root for gas efficiency: `L = sqrt(x_virtual * y_virtual)`.

#### Method ID
The method ID is the first 4 bytes of the Keccak-256 hash of the function signature. For example,
to get the method ID for `swapExactInputSingle(...)`, you would hash the full function signature
(including parameter types) and take the first 4 bytes.

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

## Appendix Mempool

### Uniswap v3 Swap Functions
When searching for "direct swaps" in the mempool data, we want to look for transactions that call
one of the function `exactInputSingle`, `exactOutputSingle`, `exactInput`, and `exactOutput` from
the [ISwapRouter.sol
contract](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/ISwapRouter.sol).
Here is also the Unsiwap v3 documentation for
[ISwapRouter](https://docs.uniswap.org/contracts/v3/reference/periphery/interfaces/ISwapRouter).

These functions have the following names with arguments:
- `exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))`
- `exactOutputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))`
- `exactInput((bytes,address,uint256,uint256,uint256))`
- `exactOutput((bytes,address,uint256,uint256,uint256))`

If we hash these strings and take the first 8 characters (4 bytes) after the `0x` of the hash we
get the signatures that we want to use to search the data field for in the raw tx data:
- `414bf389`
- `db3e2198`
- `c04b8d59`
- `f28c0498`

For `exactInputSingle` and `exactOutputSingle`, parsing is more straightforward. These functions
involve a direct swap between two tokens in a single pool, making it easier to extract relevant
information like `tokenIn`, `tokenOut`, and `amounts`.

However, the multihop functions `exactInput` and `exactOutput` are more complex. These functions
allow for swaps across multiple pools in a single transaction. The path parameter in these
functions encodes a sequence of tokens and pool fees, guiding the swap through multiple pools.

Note: If we keep the `0x` it is only possible to search for transactions where the data field
starts with `0x` followed by the 4 byte code, since the `0x` will not appear in the middle of the
hex string.

Note: We should not confuse this with the functions
`swapExactInputSingle`, `swapExactOutputSingle`, `swapExactInputMultihop`, and
`swapExactOutputMultihop` in the Uniswap implementation guide. These would be function that you
create in your own smart contract, that calls the functions in the `ISwapRouter` contract.

#### exactInputSingle(...)
- Parameters:
  - `tokenIn`: Address of the token being sent.
  - `tokenOut`: Address of the token being received.
  - `fee`: Fee tier of the pool.
  - `recipient`: Address receiving the output tokens.
  - `deadline`: Time after which the transaction will revert.
  - `amountIn`: Exact amount of `tokenIn` to swap.
  - `amountOutMinimum`: Minimum amount of `tokenOut` to receive.
  - `sqrtPriceLimitX96`: Limit on the pool's price movement.

#### exactOutputSingle(...)
- Parameters:
  - `tokenIn`: Address of the token being sent.
  - `tokenOut`: Address of the token being received.
  - `fee`: Fee tier of the pool.
  - `recipient`: Address receiving the output tokens.
  - `deadline`: Time after which the transaction will revert.
  - `amountOut`: Exact amount of `tokenOut` to receive.
  - `amountInMaximum`: Maximum amount of `tokenIn` to spend.
  - `sqrtPriceLimitX96`: Limit on the pool's price movement.

#### exactInput(...)
- Parameters:
  - `path`: Encoded path of tokens and fees representing the pools.
  - `recipient`: Address receiving the output tokens.
  - `deadline`: Time after which the transaction will revert.
  - `amountIn`: Exact amount of the input token to swap.
  - `amountOutMinimum`: Minimum amount of the output token to receive.

#### exactOutput(...)
- Parameters:
  - `path`: Encoded path of tokens and fees representing the pools to be used.
  - `recipient`: Address receiving the output tokens.
  - `deadline`: Time after which the transaction will revert.
  - `amountOut`: Exact amount of the output token to receive.
  - `amountInMaximum`: Maximum amount of the input token to spend.

## Raw tx example
Let's look at
[this](https://etherscan.io/tx/0x86f2785426ffdaf6094fabe86db607f2a8926cfef72dbba7b2a07f398e8634f5)
transaction, with the following raw tx hex string:

```
0xac9650d8000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000002a000000000000000000000000000000000000000000000000000000000000000c4f3995c67000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480000000000000000000000000000000000000000000000000000000034742a520000000000000000000000000000000000000000000000000000000060936221000000000000000000000000000000000000000000000000000000000000001b0c10feea621b82a15fd1c17e57a5748b82de2a45dc22af71264a9a92f0df6c852baca467ac44802bc604e3e06307418833f21ad3bce1f7ba5fa3abac17013af3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000104414bf389000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000001f400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060935d710000000000000000000000000000000000000000000000000000000034742a52000000000000000000000000000000000000000000000000037af8ca188d3bd5000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c000000000000000000000000000000000000000000000000037af8ca188d3bd500000000000000000000000049b1a23df0ae2ef19f5f5a63e63e4fbb3946d40700000000000000000000000000000000000000000000000000000000
```

Etherscan decodes this into the following:
```
0	data	bytes[]	0xf3995c67000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480000000000000000000000000000000000000000000000000000000034742a520000000000000000000000000000000000000000000000000000000060936221000000000000000000000000000000000000000000000000000000000000001b0c10feea621b82a15fd1c17e57a5748b82de2a45dc22af71264a9a92f0df6c852baca467ac44802bc604e3e06307418833f21ad3bce1f7ba5fa3abac17013af3
Function: selfPermit(address, uint256, uint256, uint8, bytes32, bytes32)
#	Name	Type	Data
1	token	address	0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
2	value	uint256	880028242
3	deadline	uint256	1620271649
4	v	uint8	27
5	r	bytes32	0x0c10feea621b82a15fd1c17e57a5748b82de2a45dc22af71264a9a92f0df6c85
6	s	bytes32	0x2baca467ac44802bc604e3e06307418833f21ad3bce1f7ba5fa3abac17013af3

0x414bf389000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000001f400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000060935d710000000000000000000000000000000000000000000000000000000034742a52000000000000000000000000000000000000000000000000037af8ca188d3bd50000000000000000000000000000000000000000000000000000000000000000
Function: exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))
#	Name	Type	Data
0	params.tokenIn	address	0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
0	params.tokenOut	address	0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
0	params.fee	uint24	500
0	params.recipient	address	0x0000000000000000000000000000000000000000
0	params.deadline	uint256	1620270449
0	params.amountIn	uint256	880028242
0	params.amountOutMinimum	uint256	250786276151475157
0	params.sqrtPriceLimitX96	uint160	0

0x49404b7c000000000000000000000000000000000000000000000000037af8ca188d3bd500000000000000000000000049b1a23df0ae2ef19f5f5a63e63e4fbb3946d407
Function: unwrapWETH9(uint256, address)
#	Name	Type	Data
1	amountMinimum	uint256	250786276151475157
2	recipient	address	0x49B1A23Df0aE2Ef19F5f5A63E63e4FbB3946d407
```

The logs of the transaction shows that the following events has occurred: Approval, Transfer,
Transfer, Swap, and Withdrawal.

The function `exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))`
