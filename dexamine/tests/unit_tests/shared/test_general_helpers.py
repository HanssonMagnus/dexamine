"""
This file contains unit tests for the functions in
dexamine/shared/general_helper.py.

* Author: Magnus Hansson (https://magnushansson.xyz, https://github.com/HanssonMagnus).
* License: GPL-3.0.
* Doc: https://github.com/HanssonMagnus/dexamine
"""

# Import packages
from unittest.mock import mock_open, patch
import importlib.resources as pkg_resources
import pytest

# Import modules
from dexamine.shared import general_helpers, constants


########################################################################################
# Test RPC calls with mock node requests
########################################################################################
# Test successful retrieval of transaction data
def test_get_tx_data_by_hash_success():
    """Test for general_helpers.get_tx_data_by_hash when requests.post is successful."""
    # Sample transaction hash and expected response
    tx_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    expected_response = general_helpers.get_json_test_data(
        "node_responses/tx_data.json"
    )

    # Mock the requests.post method
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        # Call the function
        response = general_helpers.get_tx_data_by_hash(
            node_url=constants.NODE_URL, tx_hash=tx_hash
        )

        # Assertions
        mocked_post.assert_called_once()
        assert response == expected_response["result"]


# Test handling of an error, such as transaction not found
def test_get_tx_data_by_hash_not_found():
    """Test for general_helpers.get_tx_data_by_hash when requests.post is not
    successful."""
    tx_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    expected_response = {"jsonrpc": "2.0", "id": 1, "result": None}

    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        response = general_helpers.get_tx_data_by_hash(
            node_url=constants.NODE_URL, tx_hash=tx_hash
        )

        assert response is None


## Test successful retrieval of transaction data
def test_get_tx_data_by_block_and_index_success():
    """Test for when requests.post is successful."""
    # Sample transaction index and block number and expected response
    block_number = "0xbcda99"
    transaction_index = "0x3b"
    expected_response = general_helpers.get_json_test_data(
        "node_responses/tx_data.json"
    )

    # Mock the requests.post method
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        # Call the function
        response = general_helpers.get_tx_data_by_block_and_index(
            node_url=constants.NODE_URL,
            block_hex=block_number,
            index_hex=transaction_index,
        )

        # Assertions
        mocked_post.assert_called_once()
        assert response == expected_response["result"]


## Test handling of an error, such as transaction not found
def test_get_tx_data_by_block_and_index_not_found():
    """Test for when requests.post is not successful."""
    block_number = "0xbcda99"
    transaction_index = "0x3b"
    expected_response = {"jsonrpc": "2.0", "id": 1, "result": None}

    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        response = general_helpers.get_tx_data_by_block_and_index(
            node_url=constants.NODE_URL,
            block_hex=block_number,
            index_hex=transaction_index,
        )

        assert response is None


## Test successful retrieval of receipt data
def test_get_receipt_data_by_hash_success():
    """Test for when requests.post is successful."""
    # Sample transaction hash and expected response
    tx_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    expected_response = general_helpers.get_json_test_data(
        "node_responses/receipt_data.json"
    )

    # Mock the requests.post method
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        # Call the function
        response = general_helpers.get_receipt_data_by_hash(
            node_url=constants.NODE_URL, tx_hash=tx_hash
        )

        # Assertions
        mocked_post.assert_called_once()
        assert response == expected_response["result"]


# Test handling of an error, such as receipt not found
def test_get_receipt_data_by_hash_not_found():
    """Test for when requests.post is not successful."""
    tx_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    expected_response = {"jsonrpc": "2.0", "id": 1, "result": None}

    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        response = general_helpers.get_receipt_data_by_hash(
            node_url=constants.NODE_URL, tx_hash=tx_hash
        )

        assert response is None


## Test successful retrieval of block data
def test_get_block_data_by_block_number_success():
    """Test for when requests.post is successful."""
    # Sample block number and expected response
    block_number = "0xbcda99"
    expected_response = general_helpers.get_json_test_data(
        "node_responses/block_data.json"
    )

    # Mock the requests.post method
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        # Call the function
        response = general_helpers.get_block_data_by_block_number(
            node_url=constants.NODE_URL, block_hex=block_number
        )

        # Assertions
        mocked_post.assert_called_once()
        assert response == expected_response["result"]


# Test handling of an error, such as receipt not found
def test_get_block_data_by_block_number_not_found():
    """Test for when requests.post is not successful."""
    block_number = "0xbcda99"
    expected_response = {"jsonrpc": "2.0", "id": 1, "result": None}

    with patch("requests.post") as mocked_post:
        mocked_post.return_value.json.return_value = expected_response

        response = general_helpers.get_block_data_by_block_number(
            node_url=constants.NODE_URL, block_hex=block_number
        )

        assert response is None


########################################################################################
# Test ABI call functions
########################################################################################


########################################################################################
# Parsing transaction logs
########################################################################################
def test_get_topics_0_normal_case():
    """Test for when logs are complete with topics 0s."""
    receipt_data = general_helpers.get_json_test_data(
        "node_responses/receipt_data.json"
    )
    logs = receipt_data["result"]["logs"]
    expected_result = [
        "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118",
        "0x98636036cb66a9c19a37435efc1e90142190214e8abeb821bdba3f2990dd4c95",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f",
    ]
    assert general_helpers.get_topics_0(logs) == expected_result


def test_get_topics_0_no_topics():
    """Test for when logs are missing topics 0s."""
    logs = [{"data": "Some data"}, {"data": "More data"}]
    expected = ["", ""]
    assert general_helpers.get_topics_0(logs) == expected


def test_get_topics_0_empty_topics():
    """Test for when topics 0 is empty."""
    logs = [
        {"topics": [], "data": "Some data"},
        {"topics": ["0xcc"], "data": "More data"},
    ]
    expected = ["", "0xcc"]
    assert general_helpers.get_topics_0(logs) == expected


def test_get_topics_0_combination():
    """Test for when topics 0 is missing, empty, and exsisting."""
    logs = [
        {"data": "Some data"},
        {"topics": ["0xcc"], "data": "More data"},
        {"topics": [], "data": "Even more data"},
        {"topics": ["0xdd", "0xee"], "data": "Yet more data"},
    ]
    expected = ["", "0xcc", "", "0xdd"]
    assert general_helpers.get_topics_0(logs) == expected


def test_get_event_index_normal_case():
    """Test for when topics0 is complete."""
    topics0 = [
        "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118",
        "0x98636036cb66a9c19a37435efc1e90142190214e8abeb821bdba3f2990dd4c95",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f",
    ]
    expected_result = [5]
    assert (
        general_helpers.get_event_indexes(topics0, [constants.UNISWAP_V3_MINT_EVENT])
        == expected_result
    )


########################################################################################
# Bytes32 parsing
########################################################################################
def test_bytes32_to_string():
    """
    Test the bytes32_to_string function to ensure it correctly decodes bytes32 data to a
    string.

    This test covers four scenarios:
    1. A normal string with trailing null bytes: Verifies that the function correctly
       decodes a bytes32 string and strips trailing null bytes.
    2. A string composed entirely of null bytes: Checks that the function returns an
       empty string when given a bytes32 value of all null bytes.
    3. A string with no null bytes: Ensures that the function correctly decodes a
       bytes32 string with no trailing null bytes and does not alter the original
       string.
    4. A string with non-UTF-8 bytes: Confirms that the function raises a
       UnicodeDecodeError when decoding bytes that cannot be interpreted as a UTF-8
       string.
    """
    # Test case with a normal string
    bytes32_data = b"Test String\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    expected_result = "Test String"
    # Should decode and strip null bytes correctly
    assert general_helpers.bytes32_to_string(bytes32_data) == expected_result

    # Test case with all null bytes
    bytes32_data_all_nulls = b"\x00" * 32
    expected_result_all_nulls = ""
    # Should return an empty string for all null bytes
    assert (
        general_helpers.bytes32_to_string(bytes32_data_all_nulls)
        == expected_result_all_nulls
    )

    # Test case with no null bytes
    bytes32_data_no_nulls = b"NoNullBytesInThisStringTesting!"
    expected_result_no_nulls = "NoNullBytesInThisStringTesting!"
    # Should return the original string if there are no null bytes
    assert (
        general_helpers.bytes32_to_string(bytes32_data_no_nulls)
        == expected_result_no_nulls
    )

    # Test case with non-UTF-8 bytes (This should raise an exception)
    bytes32_data_non_utf8 = b"\xff" * 32
    try:
        result = general_helpers.bytes32_to_string(bytes32_data_non_utf8)
        assert False, "Expected a UnicodeDecodeError"
    except UnicodeDecodeError:
        pass  # Test passes as the exception is expected


########################################################################################
# Hexadecimal parsing
########################################################################################
def test_parse_signed_int_positive():
    """Example hex for 1 in two's complement, 32 bytes."""
    hex_str = "0000000000000000000000000000000000000000000000000000000000000001"
    assert general_helpers.parse_signed_int(hex_str) == 1


def test_parse_signed_int_negative():
    """Example hex for -1 in two's complement, 32 bytes."""
    hex_str = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    assert general_helpers.parse_signed_int(hex_str) == -1


def test_parse_signed_int_max_positive():
    """Maximum positive value for 32 bytes."""
    hex_str = "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    assert general_helpers.parse_signed_int(hex_str) == 2**255 - 1


def test_parse_signed_int_min_negative():
    """Minimum negative value for 32 bytes."""
    hex_str = "8000000000000000000000000000000000000000000000000000000000000000"
    assert general_helpers.parse_signed_int(hex_str) == -(2**255)


def test_parse_signed_int_edge_case():
    """Test the conversion of a negative number represented in two's complement."""
    hex_str = "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"
    assert general_helpers.parse_signed_int(hex_str) == -2


########################################################################################
# Parse transaction type from to address
########################################################################################
def test_parse_to_type_with_contract_creation():
    """Test if to_address is "contract creation"."""
    assert general_helpers.parse_to_type(None) == "contract_creation"


def test_parse_to_type_with_mev_contract():
    """Test if a non-Uniswap address is classified as a smart contract."""
    mev_address = "0x_mev_contract_address"
    assert general_helpers.parse_to_type(mev_address) == "smart_contract"


def test_parse_to_type_with_uni_router():
    uni_address = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
    assert general_helpers.parse_to_type(uni_address) == "dex_router"


def test_parse_to_type_with_uni_universal_router_v4():
    uni_address = "0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af"
    assert general_helpers.parse_to_type(uni_address) == "dex_router"


def test_parse_to_type_with_defi_address():
    """Test if to_address is "defi", using a generic non-MEV, non-Uniswap address."""
    defi_address = "0x_defi_contract_address"
    assert general_helpers.parse_to_type(defi_address) == "smart_contract"


########################################################################################
# Test functions that load resources
########################################################################################
def test_get_json_test_data_success():
    """Test for when a correct data file has been specified."""
    sample_json_data = {"key": "value"}
    sample_json_content = '{"key": "value"}'
    m = mock_open(read_data=sample_json_content)

    with patch("importlib.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open = m
        with patch("json.load", return_value=sample_json_data):
            # Call the function with a sample file path
            result = general_helpers.get_json_test_data(
                "uniswap_v2/uniswap_v2_by_positions.json"
            )

            # Verify the file was opened correctly
            m.assert_called_once_with("r", encoding="utf-8")

            # Assert that the result matches the expected JSON data
            assert result == sample_json_data


def test_get_json_test_data_file_not_found():
    """Test for when a wrong path to a data file has been specified."""
    # Simulate a FileNotFoundError when attempting to open a non-existent file
    with patch("importlib.resources.open_text", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            # Attempt to load a file that does not exist
            general_helpers.get_json_test_data(
                "uniswap_v2_positions/non_existent_file.json"
            )


def test_get_json_abi_success():
    """Test for when a correct data file has been specified."""
    sample_json_data = {"abi": {"key": "value"}}
    sample_json_content = '{"abi": {"key": "value"}}'
    m = mock_open(read_data=sample_json_content)

    with patch("importlib.resources.files") as mock_files:
        mock_files.return_value.joinpath.return_value.open = m
        with patch("json.load", return_value=sample_json_data):
            # Call the function with a sample file path
            result = general_helpers.get_json_abi("uniswap_v2/IUniswapV2Pair.json")

            # Verify the file was opened correctly
            m.assert_called_once_with("r", encoding="utf-8")

            # Assert that the result matches the expected JSON data
            assert result == {"key": "value"}


def test_get_json_test_abi_not_found():
    """Test for when a wrong path to a data file has been specified."""
    # Simulate a FileNotFoundError when attempting to open a non-existent file
    with patch("importlib.resources.open_text", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            # Attempt to load a file that does not exist
            general_helpers.get_json_abi("uniswap_v2/non_existent_file.json")


def test_get_csv_test_data_as_string():
    """Test for loading csv data as a string."""
    # Mock CSV content that you expect to read from the file
    mock_csv_content = "column1,column2\nvalue1,value2\nvalue3,value4"
    m = mock_open(read_data=mock_csv_content)

    # Patch the files method from importlib.resources
    with patch("importlib.resources.files") as mocked_files:
        mocked_files.return_value.joinpath.return_value.open = m
        # Call the function with the path to the test data file
        result = general_helpers.get_csv_test_data_as_string("uniswap_v2/myfile.csv")

        # Verify that the files method was called correctly
        mocked_files.assert_called_once()

        # Verify that the file was opened correctly
        m.assert_called_once_with("r", encoding="utf-8")

        # Assert that the result matches the mock CSV content
        assert result == mock_csv_content


########################################################################################
# Transforming files
########################################################################################
def test_chifra_csv_to_json():
    """Transform a chifra list to json format without duplicates."""
    expected = general_helpers.get_json_test_data(
        "uniswap_v2_positions/uniswap_v2_by_positions.json"
    )
    csv_content = general_helpers.get_csv_test_data_as_string(
        "uniswap_v2_positions/uniswap_v2_by_positions.csv"
    )
    assert general_helpers.chifra_csv_to_json(csv_content) == expected
