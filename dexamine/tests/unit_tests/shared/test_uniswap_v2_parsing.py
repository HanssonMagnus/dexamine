"""
This file contains unit tests for the functions in
dexamine/shared/uniswap_v2_parsing.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from typing import Any

# Import modules
from dexamine.shared import constants, uniswap_v2_parsing

POOL = constants.UNISWAP_V2_USDC_WETH_ADDRESS
OTHER_POOL = "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"
TX_HASH = "0x" + "ab" * 32


def _log(address: str, topic_0: str) -> dict[str, Any]:
    return {"address": address, "topics": [topic_0], "transactionHash": TX_HASH}


########################################################################################
# Event presence checks
########################################################################################
def test_has_uniswap_v2_swap_event():
    assert uniswap_v2_parsing.has_uniswap_v2_swap_event(
        [constants.UNISWAP_V2_SYNC_EVENT, constants.UNISWAP_V2_SWAP_EVENT]
    )
    assert not uniswap_v2_parsing.has_uniswap_v2_swap_event(
        [constants.UNISWAP_V2_SYNC_EVENT]
    )
    assert not uniswap_v2_parsing.has_uniswap_v2_swap_event([])


def test_has_uniswap_v2_mint_event():
    assert uniswap_v2_parsing.has_uniswap_v2_mint_event(
        [constants.UNISWAP_V2_MINT_EVENT]
    )
    assert not uniswap_v2_parsing.has_uniswap_v2_mint_event(
        [constants.UNISWAP_V2_BURN_EVENT]
    )


def test_has_uniswap_v2_burn_event():
    assert uniswap_v2_parsing.has_uniswap_v2_burn_event(
        [constants.UNISWAP_V2_BURN_EVENT]
    )
    assert not uniswap_v2_parsing.has_uniswap_v2_burn_event(
        [constants.UNISWAP_V2_MINT_EVENT]
    )


def test_event_checks_do_not_confuse_v2_and_v3_topics():
    """The v2 and v3 event signatures are distinct hashes."""
    v3_topics = [
        constants.UNISWAP_V3_SWAP_EVENT,
        constants.UNISWAP_V3_MINT_EVENT,
        constants.UNISWAP_V3_BURN_EVENT,
    ]
    assert not uniswap_v2_parsing.has_uniswap_v2_swap_event(v3_topics)
    assert not uniswap_v2_parsing.has_uniswap_v2_mint_event(v3_topics)
    assert not uniswap_v2_parsing.has_uniswap_v2_burn_event(v3_topics)


########################################################################################
# Sync event ordering
########################################################################################
def test_sync_event_is_before_event_true():
    """A sync event from the same pool immediately before the swap is valid."""
    logs = [
        _log(POOL, constants.UNISWAP_V2_SYNC_EVENT),
        _log(POOL, constants.UNISWAP_V2_SWAP_EVENT),
    ]
    assert uniswap_v2_parsing.sync_event_is_before_event(logs, 1) is True


def test_sync_event_is_before_event_false_when_event_is_first():
    """There is nothing before log index 0, so the ordering rule fails."""
    logs = [_log(POOL, constants.UNISWAP_V2_SWAP_EVENT)]
    assert uniswap_v2_parsing.sync_event_is_before_event(logs, 0) is False


def test_sync_event_is_before_event_false_for_different_pool():
    """A sync event from another pool does not satisfy the ordering rule."""
    logs = [
        _log(OTHER_POOL, constants.UNISWAP_V2_SYNC_EVENT),
        _log(POOL, constants.UNISWAP_V2_SWAP_EVENT),
    ]
    assert uniswap_v2_parsing.sync_event_is_before_event(logs, 1) is False


def test_sync_event_is_before_event_false_for_non_sync_predecessor():
    """The preceding log must be a sync event, not any other event."""
    logs = [
        _log(POOL, constants.UNISWAP_V2_MINT_EVENT),
        _log(POOL, constants.UNISWAP_V2_SWAP_EVENT),
    ]
    assert uniswap_v2_parsing.sync_event_is_before_event(logs, 1) is False
