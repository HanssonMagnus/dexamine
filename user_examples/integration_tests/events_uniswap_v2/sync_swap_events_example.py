# Test if the sync event emits reserves before or after the swap has taken place.
#
# Data:
# Analysis of the second swap from this trade on Uniswap v2:
# https://etherscan.io/tx/0x63a1a7ee5fbb6bbe869e18601b67897d4516e53596f0b90b609ee3ae301163ca

# Import packages
from decimal import Decimal, getcontext

# Set precision
getcontext().prec = 19

# Data from sync event
reserve0 = Decimal("34380566947687148691700151")
reserve1 = Decimal("729414612205345013242")

# Data from subsequent swap event
amount0In = Decimal("456056313444833958558829")
amount0Out = 0

amount1In = 0
amount1Out = Decimal("9776299507275846209")

# Change the reserve 0 and reserve 1 such that is was "before" the swap
reserve0 = reserve0 - amount0In
reserve1 = reserve1 + amount1Out

print(reserve0)
print(reserve1)

# Calculate amount1Out from the liquidity pools and the amount of token 0 added to the pool
fee = Decimal("0.997")
amount1Out_check = amount0In * fee * reserve1 / (reserve0 + amount0In * fee)

# Check to see if dyt and dyt_check are the same
check = [amount1Out, amount1Out_check]
print(check)
print("The amounts are the same:", amount1Out == amount1Out_check)

# Output:
# [Decimal('9776299507275846209'), Decimal('9776299507275846209')]
# The amounts are the same: True
#
# Conclusion:
# The sync event emits the reserves after the swap has taken place.
