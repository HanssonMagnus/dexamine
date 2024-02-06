| Function | Total Calls | Total Time | Cumulative Time | Description |
|----------|-------------|------------|-----------------|-------------|
| `<string>:1(<module>)` | 1 | 59.036 | 59.036 | Represents the entire script execution, typically the script's entry point. |
| `keccak.py:35(keccak256)` | 40392 | 1.542 | 1.551 | Computes the Keccak-256 hash, a cryptographic hash function used in Ethereum. |
| `keccak.py:143(new)` | 40392 | 0.009 | 1.551 | Creates a new hash object, often used in conjunction with `keccak256` for hash computations. |
| `abi.py:712(map_abi_data)` | 40392 | 0.975 | 1.484 | Maps ABI data, part of decoding Ethereum smart contract ABI data. |
| `abi.py:749(abi_data_tree)` | 80784 | 0.509 | 1.484 | Builds a tree from ABI data, aiding in interpreting complex contract data structures. |
| `abi.py:760(<listcomp>)` | 40392 | 0.509 | 1.484 | A list comprehension within `abi_data_tree`, processes elements of the data tree. |
| `uniswap_v2_parsing.py:29(get_erc20_symbol)` | 20196 | 0.625 | 1.172 | Retrieves the symbol of an ERC-20 token, used in Uniswap V2 transactions. |
| `uniswap_v2_parsing.py:10(get_v2_pair)` | 20196 | 0.547 | 1.172 | Gets details about a Uniswap V2 pair, like the tokens involved. |
| `client.py:1331(getresponse)` | 20196 | 0.391 | 1.017 | Handles HTTP responses, likely from API calls or web requests. |
| `client.py:311(begin)` | 20196 | 0.626 | 1.017 | Initiates an HTTP connection, typically the start of a web request or API call. |
