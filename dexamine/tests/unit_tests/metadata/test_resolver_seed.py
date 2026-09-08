"""Contracts for supplying metadata through the public resolver API."""

from unittest.mock import patch

import pytest

from dexamine import DexamineSession
from dexamine.metadata import Erc20Metadata, V2PairMetadata, V3PoolMetadata
from dexamine.shared import constants

USDC = constants.USDC_TOKEN_ADDRESS
WETH = constants.WETH_TOKEN_ADDRESS
V2_PAIR = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
V3_POOL = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"


def test_seeded_metadata_is_available_offline_with_normalized_addresses():
    resolver = DexamineSession.from_node_url("http://unused.invalid").metadata
    tokens = {
        USDC.lower(): Erc20Metadata("USDC", 6),
        WETH.lower(): Erc20Metadata("WETH", 18),
    }
    with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")):
        resolver.seed(
            erc20=tokens,
            v2_pairs={
                V2_PAIR.lower(): V2PairMetadata(USDC.lower(), WETH.lower(), "UNI-V2")
            },
            v3_pools={
                V3_POOL.lower(): V3PoolMetadata(USDC.lower(), WETH.lower(), "UniV3")
            },
        )
        tokens.clear()
        assert resolver.get_erc20(USDC) == Erc20Metadata("USDC", 6)
        assert resolver.get_erc20(WETH.lower()) == Erc20Metadata("WETH", 18)
        assert resolver.get_uniswap_v2_pair(V2_PAIR) == V2PairMetadata(
            USDC, WETH, "UNI-V2"
        )
        assert resolver.get_uniswap_v3_pool(V3_POOL.lower()) == V3PoolMetadata(
            USDC, WETH, "UniV3"
        )


def test_reseeding_updates_supplied_entries_and_preserves_other_metadata():
    resolver = DexamineSession.from_node_url("http://unused.invalid").metadata
    with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")):
        resolver.seed(
            erc20={USDC: Erc20Metadata("old", 18), WETH: Erc20Metadata("WETH", 18)}
        )
        resolver.seed(erc20={USDC.lower(): Erc20Metadata("USDC", 6)})
        resolver.seed()
        assert resolver.get_erc20(USDC) == Erc20Metadata("USDC", 6)
        assert resolver.get_erc20(WETH) == Erc20Metadata("WETH", 18)


@pytest.mark.parametrize("invalid", ["key", "token0", "token1"])
def test_invalid_seed_does_not_partially_change_the_cache(invalid):
    resolver = DexamineSession.from_node_url("http://unused.invalid").metadata
    resolver.seed(erc20={USDC: Erc20Metadata("USDC", 6)})
    with pytest.raises(ValueError):
        resolver.seed(
            erc20={USDC: Erc20Metadata("replacement", 18)},
            v3_pools={
                "invalid" if invalid == "key" else V3_POOL: V3PoolMetadata(
                    "invalid" if invalid == "token0" else USDC,
                    "invalid" if invalid == "token1" else WETH,
                    "UniV3",
                )
            },
        )
    assert resolver.get_erc20(USDC) == Erc20Metadata("USDC", 6)


def test_seed_keeps_normal_endpoint_lookup_for_missing_metadata():
    resolver = DexamineSession.from_node_url("http://unused.invalid").metadata
    resolver.seed(erc20={USDC: Erc20Metadata("USDC", 6)})
    with patch(
        "dexamine.shared.general_helpers.get_erc20_symbol", return_value=("WETH", 18)
    ) as lookup:
        assert resolver.get_erc20(WETH.lower()) == Erc20Metadata("WETH", 18)
        assert resolver.get_erc20(WETH) == Erc20Metadata("WETH", 18)
        lookup.assert_called_once()
        assert lookup.call_args.kwargs["token_address"] == WETH
