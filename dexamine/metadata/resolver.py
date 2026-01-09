"""
Cached metadata resolver for pools and ERC-20 tokens.

This is a connector-style class (allowed to hold state) intended to be instantiated
per-process (e.g. inside each multiprocessing worker).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from web3 import Web3

from dexamine.shared import constants, general_helpers

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
    erc20_abi: dict
    erc20_bytes32_abi: dict
    uniswap_v2_pair_abi: dict
    uniswap_v3_pair_abi: dict
    _w3: Web3 = field(init=False, repr=False)
    _erc20_cache: dict[str, Erc20Metadata] = field(default_factory=dict, repr=False)
    _v2_pair_cache: dict[str, V2PairMetadata] = field(default_factory=dict, repr=False)
    _v3_pool_cache: dict[str, V3PoolMetadata] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._w3 = Web3(Web3.HTTPProvider(self.node_url))

    def _checksum(self, address: str) -> str:
        return Web3.to_checksum_address(address)

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

        pair_contract = self._w3.eth.contract(address=key, abi=self.uniswap_v2_pair_abi)
        token0 = pair_contract.functions.token0().call()
        token1 = pair_contract.functions.token1().call()

        # V2 pairs are ERC-20 LP tokens, so symbol() exists.
        dex_contract = self._w3.eth.contract(address=key, abi=self.erc20_abi)
        dex_symbol = dex_contract.functions.symbol().call()

        meta = V2PairMetadata(token0=token0, token1=token1, dex_symbol=dex_symbol)
        self._v2_pair_cache[key] = meta
        return meta

    def get_uniswap_v3_pool(self, pool_address: str) -> V3PoolMetadata:
        key = self._checksum(pool_address)
        cached = self._v3_pool_cache.get(key)
        if cached is not None:
            return cached

        pool_contract = self._w3.eth.contract(address=key, abi=self.uniswap_v3_pair_abi)
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

