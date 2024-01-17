# Imports
from pprint import pprint
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
from eth_utils import encode_hex, to_bytes

# Import scripts
from shared import general_helpers
from shared import constants
from parsers.uniswap_v3 import parse_uni_v3_events

# Function to convert complex objects to JSON-friendly format
def json_friendly(data):
    if isinstance(data, bytes):
        return encode_hex(data)
    elif hasattr(data, '__dict__'):
        return {key: json_friendly(value) for key, value in data.__dict__.items()}
    elif isinstance(data, (list, tuple)):
        return [json_friendly(item) for item in data]
    else:
        return data

# Raw London (EIP-1559) tx as hex string (the signed transaction to decode)
raw_1559_tx = "0x02f8b10181a88405f5e100850402a4432082b46d94ed5af388653567af2f388e6224dc7c4b3241c54480b844a22cb465000000000000000000000000ef887e8b1c06209f59e8ae55d0e625c9373443760000000000000000000000000000000000000000000000000000000000000001c001a03525632fa005bc5f7ea221641bd68d2852c54955535d5323d4c69f3e1da53e87a017fad5931f8e547dd0659a41b8ae6763b0fe0f268d2ffe09f051d71d48c47c75"

# Raw legacy tx as hex string (the signed transaction to decode)
raw_legacy_tx = "0xf8a910850684ee180082e48694a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4880b844a9059cbb000000000000000000000000b8b59a7bc828e6074a4dd00fa422ee6b92703f9200000000000000000000000000000000000000000000000000000000010366401ba0e2a4093875682ac6a1da94cdcc0a783fe61a7273d98e1ebfe77ace9cab91a120a00f553e48f3496b7329a7c0008b3531dd29490c517ad28b0e6c1fba03b79a1dee"

# Convert the hex string to bytes
signed_tx_as_bytes = to_bytes(hexstr=raw_1559_tx)
signed_tx_as_bytes = to_bytes(hexstr=raw_legacy_tx)

# Deserialize the transaction using the latest transaction builder:
decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)


# Transform to dict
decoded_tx = decoded_tx.__dict__

pprint(decoded_tx)

pprint(decoded_tx.keys())

pprint(type(decoded_tx))
pprint(type(decoded_tx['_inner']))
#pprint(json_friendly(decoded_tx))

# Show keys `dict_keys(['type_id', '_inner', 'sender'])`
#decoded_tx.__dict__.keys()

# {'type_id': 2, '_inner': DynamicFeeTransaction(chain_id=1, nonce=4, max_priority_fee_per_gas=2500000000, max_fee_per_gas=118977454018, gas=45000, to=b'\xe9\xcb\...', value=0, data=b'', access_list=(), y_parity=1, r=23532..., s=28205...)}

# 4) the (human-readable) sender's address:
#sender = encode_hex(decoded_tx.sender)
#pprint(sender)
# 0xe9cb1f...

# 5) the (human-readable) data:
#data = encode_hex(decoded_tx.data)
#pprint(data)
# 0xe9cb1f...
