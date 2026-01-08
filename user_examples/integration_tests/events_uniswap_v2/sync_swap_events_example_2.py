# Test if the sync event emits reserves before or after the swap has taken place.
#
# Data:
# Analysis of the second swap from this trade on Uniswap v2:
# https://etherscan.io/tx/0x63a1a7ee5fbb6bbe869e18601b67897d4516e53596f0b90b609ee3ae301163ca

# Import packages
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Set precision
getcontext().prec = 28

# Data from sync event
reserve0 = Decimal("29860286283991007650")
reserve1 = Decimal("427341690080835907187")

# Data from subsequent swap event
# This data is a bit strange as Token0 is both deposited and withdrawn from the liquidity pool.
#
# Token0 has a "net" out and Token1 has only a deposit.
amount0In = Decimal("2081147327526053")
amount0Out = Decimal("696961612401492081")
# amount0Out = amount0Out - amount0In

amount1In = Decimal("9776299507275846209")
amount1Out = 0


# Change the reserve 0 and reserve 1 such that is was "before" the swap
reserve0 = reserve0 - amount0In + amount0Out
reserve1 = reserve1 - amount1In

print(reserve0)
print(reserve1)

# Calculate amount1Out from the liquidity pools and the amount of token 0 added to the pool
fee = Decimal("0.997")
amount0Out_check = amount1In * fee * reserve0 / (reserve1 + amount1In * fee)
amount0Out_check_rounded = amount0Out_check.quantize(
    Decimal("1"), rounding=ROUND_HALF_UP
)

# Check to see if dyt and dyt_check are the same
check = [amount0Out, amount0Out_check_rounded]
print(check)
print("The amounts are the same:", amount0Out == amount0Out_check_rounded)

# Output:
# [Decimal('696961612401492081'), Decimal('696961612401492081')]
# The amounts are the same: True
#
# Conclusion:
# 1. The sync event emits the reserves after the swap has taken place.
# 2. This is a bit strange but in this transaction amount1In was traded for amount0Out, but then
# also, "afterwards",  amount0In was added to the LP. This is puzzling.
#
# From a similar situation:
# https://ethereum.stackexchange.com/questions/99553/how-to-understand-the-swap-event-payload
#
# Safemoon contract actually transfers to recipient specified amount of tokens minus 10% (5% tax fee
# and 5% liquidity fee) 208940457743532637 - 10% = 188046411969179375 and emits Transfer event.
# Then, PancakePair _swap function emits Swap event with base value of Amount0Out 208940457743532637
#
# Amount0In is greater than zero because Safemoon contract returns part of safemoon tokens as a
# liquidity pair on Pancake Swap.
