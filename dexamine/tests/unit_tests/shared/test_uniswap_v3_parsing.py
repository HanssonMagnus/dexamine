"""
This file contains unit tests for the functions in
dexamine/shared/uniswap_v3_parsing.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import modules
from dexamine.shared import constants, general_helpers, uniswap_v3_parsing


########################################################################################
# Event presence checks
########################################################################################
def test_has_uniswap_v3_swap_event():
    assert uniswap_v3_parsing.has_uniswap_v3_swap_event(
        [constants.UNISWAP_V3_SWAP_EVENT]
    )
    assert not uniswap_v3_parsing.has_uniswap_v3_swap_event(
        [constants.UNISWAP_V3_MINT_EVENT]
    )
    assert not uniswap_v3_parsing.has_uniswap_v3_swap_event([])


def test_has_uniswap_v3_mint_event():
    assert uniswap_v3_parsing.has_uniswap_v3_mint_event(
        [constants.UNISWAP_V3_MINT_EVENT]
    )
    assert not uniswap_v3_parsing.has_uniswap_v3_mint_event(
        [constants.UNISWAP_V3_BURN_EVENT]
    )


def test_has_uniswap_v3_burn_event():
    assert uniswap_v3_parsing.has_uniswap_v3_burn_event(
        [constants.UNISWAP_V3_BURN_EVENT]
    )
    assert not uniswap_v3_parsing.has_uniswap_v3_burn_event(
        [constants.UNISWAP_V3_SWAP_EVENT]
    )


def test_event_checks_do_not_confuse_v3_and_v2_topics():
    """The v3 and v2 event signatures are distinct hashes."""
    v2_topics = [
        constants.UNISWAP_V2_SWAP_EVENT,
        constants.UNISWAP_V2_MINT_EVENT,
        constants.UNISWAP_V2_BURN_EVENT,
    ]
    assert not uniswap_v3_parsing.has_uniswap_v3_swap_event(v2_topics)
    assert not uniswap_v3_parsing.has_uniswap_v3_mint_event(v2_topics)
    assert not uniswap_v3_parsing.has_uniswap_v3_burn_event(v2_topics)


########################################################################################
# Event checks against a recorded receipt
########################################################################################
def test_event_checks_against_recorded_receipt():
    """
    The recorded receipt creates the USDC/WETH 0.05% pool and mints the first
    position, so it contains a v3 mint event but no swap or burn event.
    """
    receipt = general_helpers.get_json_test_data("node_responses/receipt_data.json")
    topics_0 = general_helpers.get_topics_0(receipt["result"]["logs"])

    assert uniswap_v3_parsing.has_uniswap_v3_mint_event(topics_0)
    assert not uniswap_v3_parsing.has_uniswap_v3_swap_event(topics_0)
    assert not uniswap_v3_parsing.has_uniswap_v3_burn_event(topics_0)
