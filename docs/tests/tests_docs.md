# Tests docs

## End-to-end tests

## Integration tests

#### Sync event Uniswap v2
The sync event in the logs outputs the reserves of token0 and token1 in the liquidity pool. The
sync function is called each time a mint, burn, or swap event takes place. However, it is unclear
from the Uniswap v2 docs if the sync event emits the reserves after the mint, burn, or swap has
taken place.

As it turns out, the sync event emits the inventory of the liquidity pool after the swap has taken
place.

## Unit tests
