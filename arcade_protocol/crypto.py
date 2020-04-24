import os
from web3 import (
    Account,
)
from eth_account.messages import (
    encode_intended_validator,
)
from eth_abi.packed import (
    encode_abi_packed,
)
from hexbytes import (
    HexBytes,
)


def sign_score(key, validator, game_id, user, score):
    game_id = HexBytes(game_id)
    types = ['bytes32', 'address', 'uint256']
    values = [game_id, user, score]
    encoded_values = encode_abi_packed(types, values)
    message = encode_intended_validator(
        validator_address=validator,
        primitive=encoded_values,
    )
    signed = Account.sign_message(message, key)
    vrs = {
        'v': signed['v'],
        'r': HexBytes(signed['r']).hex(),
        's': HexBytes(signed['s']).hex(),
    }
    return vrs


def random_32bytes():
    value = HexBytes(os.urandom(32))
    return value.hex()
