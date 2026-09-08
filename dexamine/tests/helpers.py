"""
Shared helpers for the dexamine test suite.

These utilities let the parser tests run entirely offline: `make_metadata_resolver`
returns a real `MetadataResolver` whose caches are pre-populated, so every metadata
lookup is a cache hit and no JSON-RPC call is ever made.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

from __future__ import annotations

from dexamine.metadata.resolver import (
    Erc20Metadata,
    MetadataResolver,
    V2PairMetadata,
    V3PoolMetadata,
)

# A node URL that is never contacted: all lookups are served from the caches below.
UNUSED_NODE_URL = "http://unused.invalid"


def word(value: int) -> str:
    """Encode a non-negative integer as a 32-byte ABI word (64 hex characters)."""
    if value < 0:
        raise ValueError(f"word() takes non-negative values, got {value}")
    return f"{value:064x}"


def signed_word(value: int) -> str:
    """Encode a signed integer as a two's-complement 32-byte ABI word."""
    return f"{value & (2**256 - 1):064x}"


def make_metadata_resolver(
    *,
    erc20: dict[str, tuple[str, int]] | None = None,
    v2_pairs: dict[str, tuple[str, str, str]] | None = None,
    v3_pools: dict[str, tuple[str, str, str]] | None = None,
) -> MetadataResolver:
    """
    Build a MetadataResolver with pre-populated caches.

    Args:
        erc20: token address -> (symbol, decimals).
        v2_pairs: pair address -> (token0, token1, dex_symbol).
        v3_pools: pool address -> (token0, token1, dex_symbol).

    Addresses are used verbatim as cache keys, so the parsers must be given the same
    spelling. Pool and pair addresses are checksummed by the resolver, so pass them in
    checksum form; token addresses are only used as dictionary keys here.
    """
    resolver = MetadataResolver(
        node_url=UNUSED_NODE_URL,
        erc20_abi=[],
        erc20_bytes32_abi=[],
        uniswap_v2_pair_abi=[],
        uniswap_v3_pair_abi=[],
    )

    for address, (symbol, decimals) in (erc20 or {}).items():
        resolver._erc20_cache[address] = (
            Erc20Metadata(  # pylint: disable=protected-access
                symbol=symbol, decimals=decimals
            )
        )
    for address, (token0, token1, dex_symbol) in (v2_pairs or {}).items():
        resolver._v2_pair_cache[address] = (
            V2PairMetadata(  # pylint: disable=protected-access
                token0=token0, token1=token1, dex_symbol=dex_symbol
            )
        )
    for address, (token0, token1, dex_symbol) in (v3_pools or {}).items():
        resolver._v3_pool_cache[address] = (
            V3PoolMetadata(  # pylint: disable=protected-access
                token0=token0, token1=token1, dex_symbol=dex_symbol
            )
        )

    return resolver
