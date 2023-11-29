# Scripts Documentation - `node-data` Project

## Uniswap v2

#### parse_uni_v2_events.py
This file contains parsers for liquidity taking and liquidity provision for Uniswap v2.

##### `def parse_v2_trade(logs, swap_index, uniswap_v2_erc20_abi, uniswap_v2_pair_abi)`:
In this function, the "net traded amounts" are calculated as,
```
dxt = amount0In - amount0Out # change in xt (USDC liquidity pool at t)
dyt = amount1In - amount1Out # change in yt (wETH liquidity pool at t)
```
For most currency pairs, if there is an input of token0 the output of token0 is 0 and vice versa.
Therefore, this "net trade" calculation is perfectly fine.

However, this has some implications for certain currency pairs. There are ERC20 tokens that has
built in functionality that is called when you interact with the protocol. For example, the
Safemoon contract returns part of Safemoon tokens to the liquidity pair on the DEX. Therefore, you
can have a swap event that looks like the following,
```
amount0In = 2081147327526053
amount0Out = 696961612401492081

amount1In = 9776299507275846209
amount1Out = 0
```
Where `Amount0In` is greater than zero. Here the trader inputs `9776299507275846209` but only
receives `696961612401492081` since there is some other latent cost to the specific ERC20 protocol.

To mitigate any potential issues here, I would recommend that you understand the ERC20 protocol
that you are analyzing. You can also run `./tests/integration_tests/sync_swap_events.py` and
investigate if there are any edge cases.

## Uniswap v3
