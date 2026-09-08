"""
Cached metadata resolver for pools and ERC-20 tokens.

This is a connector-style class (allowed to hold state) intended to be instantiated
per-process (e.g. inside each multiprocessing worker).
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import cast

from eth_typing import ABI, ChecksumAddress
from web3 import Web3

from dexamine.shared import constants, general_helpers
from dexamine.shared.general_helpers import Abi

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Erc20Metadata:
    symbol: str
    decimals: int


@dataclass(frozen=True, slots=True)
class V2PairMetadata:
    token0: str
    token1: str
    dex_symbol: str


@dataclass(frozen=True, slots=True)
class V3PoolMetadata:
    token0: str
    token1: str
    dex_symbol: str


@dataclass
class MetadataResolver:
    node_url: str
    erc20_abi: Abi
    erc20_bytes32_abi: Abi
    uniswap_v2_pair_abi: Abi
    uniswap_v3_pair_abi: Abi
    _w3: Web3 = field(init=False, repr=False)
    _erc20_cache: dict[str, Erc20Metadata] = field(default_factory=dict, repr=False)
    _v2_pair_cache: dict[str, V2PairMetadata] = field(default_factory=dict, repr=False)
    _v3_pool_cache: dict[str, V3PoolMetadata] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._w3 = Web3(Web3.HTTPProvider(self.node_url))

    def _checksum(self, address: str) -> ChecksumAddress:
        return Web3.to_checksum_address(address)

    def seed(
        self,
        *,
        erc20: Mapping[str, Erc20Metadata] | None = None,
        v2_pairs: Mapping[str, V2PairMetadata] | None = None,
        v3_pools: Mapping[str, V3PoolMetadata] | None = None,
    ) -> None:
        """Cache caller-supplied metadata without making network requests.

        Keys and pool token addresses are normalized to checksum form. Supplied
        entries replace existing values; other cached entries are retained. The
        input mappings are copied, and metadata values are immutable. All addresses
        are validated before any cache is changed; invalid addresses raise ValueError.

        This does not enable an offline-only mode: a subsequent cache miss queries
        the configured endpoint as usual. Callers are responsible for the accuracy
        and historical provenance of the metadata they supply.
        """
        tokens: dict[str, Erc20Metadata] = {
            self._checksum(address): metadata
            for address, metadata in (erc20 or {}).items()
        }
        pairs: dict[str, V2PairMetadata] = {
            self._checksum(address): replace(
                metadata,
                token0=self._checksum(metadata.token0),
                token1=self._checksum(metadata.token1),
            )
            for address, metadata in (v2_pairs or {}).items()
        }
        pools: dict[str, V3PoolMetadata] = {
            self._checksum(address): replace(
                metadata,
                token0=self._checksum(metadata.token0),
                token1=self._checksum(metadata.token1),
            )
            for address, metadata in (v3_pools or {}).items()
        }
        self._erc20_cache.update(tokens)
        self._v2_pair_cache.update(pairs)
        self._v3_pool_cache.update(pools)

    def get_erc20(self, token_address: str) -> Erc20Metadata:
        key = self._checksum(token_address)
        cached = self._erc20_cache.get(key)
        if cached is not None:
            return cached

        # Reuse existing behavior (bytes32 symbol fallback) but cache the result.
        symbol, decimals = general_helpers.get_erc20_symbol(
            node_url=self.node_url,
            token_address=key,
            erc20_abi=self.erc20_abi,
            erc20_bytes32_abi=self.erc20_bytes32_abi,
        )
        meta = Erc20Metadata(symbol=symbol, decimals=decimals)
        self._erc20_cache[key] = meta
        return meta

    def get_uniswap_v2_pair(self, pair_address: str) -> V2PairMetadata:
        key = self._checksum(pair_address)
        cached = self._v2_pair_cache.get(key)
        if cached is not None:
            return cached

        pair_contract = self._w3.eth.contract(
            address=key, abi=cast(ABI, self.uniswap_v2_pair_abi)
        )
        token0 = pair_contract.functions.token0().call()
        token1 = pair_contract.functions.token1().call()

        # V2 pairs are ERC-20 LP tokens, so symbol() exists.
        dex_contract = self._w3.eth.contract(address=key, abi=cast(ABI, self.erc20_abi))
        dex_symbol = dex_contract.functions.symbol().call()

        meta = V2PairMetadata(token0=token0, token1=token1, dex_symbol=dex_symbol)
        self._v2_pair_cache[key] = meta
        return meta

    def get_uniswap_v3_pool(self, pool_address: str) -> V3PoolMetadata:
        key = self._checksum(pool_address)
        cached = self._v3_pool_cache.get(key)
        if cached is not None:
            return cached

        pool_contract = self._w3.eth.contract(
            address=key, abi=cast(ABI, self.uniswap_v3_pair_abi)
        )
        token0 = pool_contract.functions.token0().call()
        token1 = pool_contract.functions.token1().call()

        factory_address = pool_contract.functions.factory().call()
        if factory_address == constants.UNISWAP_V3_FACTORY_ADDRESS:
            dex_symbol = "UniV3"
        else:
            dex_symbol = factory_address

        meta = V3PoolMetadata(token0=token0, token1=token1, dex_symbol=dex_symbol)
        self._v3_pool_cache[key] = meta
        return meta
