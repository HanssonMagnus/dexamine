# Parsers Documentation - `node-data` Project

## Mempool data
Single Transaction Scope: Each Ethereum transaction, as seen in the mempool, is a single atomic
action. It can involve complex operations, but these are all executed within the scope of that
single transaction. If a transaction involves a call to a contract which then interacts with
Uniswap, it's still part of the same transaction.

Initiator vs. Nested Calls: The initiator of a transaction is the externally owned account (EOA)
that sends the transaction to the network. A contract called by this transaction can execute
further logic, like swapping tokens on Uniswap. However, this all happens within the context of the
original transaction; there isn't a new, separate transaction sent to the network by the contract.

## Complex Transactions and Smart Contract Interactions
Smart Contracts Calling Other Contracts: In Ethereum, a transaction can involve a smart contract
that, in turn, calls other contracts. For instance, a single transaction might interact with a DeFi
protocol that then executes trades on Uniswap.

Encoded Function Calls: The _data field contains the encoded function call(s). For a simple
transaction, this is just one function call (method ID + parameters). However, for more complex
transactions, the _data field might represent a sequence of function calls.

Proxy Contracts or Multi-Call Patterns: Some transactions use proxy contracts or implement a
multi-call pattern, allowing multiple actions to be batched into a single transaction. The _data
field in such cases will contain encoded information representing these multiple calls.

## Decoding Complex Transactions
To decode complex transactions involving multiple swaps or actions, you need a more sophisticated
approach:

Understanding the Contract's Logic: You must understand the logic of the contract initiating the
transaction. This often involves looking at the contract's source code (if available) and
understanding how it encodes multiple actions.

Decoding Nested Calls: If the transaction involves a contract that makes nested calls to other
contracts (like Uniswap), you will need to decode each nested call. This often requires parsing the
_data field to extract each call, which can be complex depending on how the contract encodes these
calls.

Using Contract ABIs: You will need the ABIs of all involved contracts to correctly decode the
nested function calls. The ABIs define how different function calls are encoded.

Handling Custom Logic: Some contracts may have custom logic that does not follow standard encoding
patterns. In such cases, understanding the contract's specific implementation is crucial.

## Capturing Swaps in the Mempool Data
#### Direct Swaps
If an EOA directly interacts with Uniswap (e.g., a direct token swap), you will see this as a
transaction with Uniswap's contract address as the recipient and the swap method's ID in the "data"
field.

- In a direct token swap transaction with Uniswap, an externally owned account (EOA) interacts
directly with the Uniswap contract.
- Such a transaction will contain only one swap operation, and the _data field of this transaction
will have the method ID corresponding to the specific swap function of Uniswap, along with its
parameters.
- The recipient (_to) of this transaction will be the Uniswap contract address.

#### Indirect Swaps
If the EOA interacts with another contract (say, a DeFi protocol) which then calls Uniswap, the
transaction will be sent to the DeFi protocol's contract address. The "data" field will contain the
encoded function call to this contract. The Uniswap swap will be a part of the internal logic of
this contract and not directly visible in the transaction's "data" field as sent to the mempool.

- If a transaction involves more than one swap, it is typically part of a complex transaction. This
happens when the transaction is sent to a smart contract (not directly to Uniswap), which then
executes multiple actions based on its internal logic.
- These actions could include multiple swaps on Uniswap or other decentralized exchanges (DEXs).
The details of these swaps are encoded within the contract's logic and are not directly visible in
the transaction's _data field sent to the Ethereum network.
- The smart contract essentially bundles multiple operations, including swaps, into a single
Ethereum transaction. This is common in DeFi protocols where a series of token interactions (like
swaps, liquidity provision, etc.) are executed in a single transaction for efficiency and
composability.

## Parsing Uniswap Swaps
Method IDs: To capture direct Uniswap swaps, you can search for specific method IDs in the "data"
field. This will identify transactions that are directly calling Uniswap swap functions.

Decoding Complex Transactions: For transactions that interact with contracts which then call
Uniswap, you'll need a more complex decoding process. You'd have to decode the initial function
call and understand the contract's internal logic to see if it results in a Uniswap swap.

Limitations: With just the mempool data, you can easily identify direct swaps but may not be able
to fully capture or decode indirect swaps (i.e., swaps initiated by a contract as part of its
internal logic) without additional context or understanding of the specific contracts involved.

