from web3 import (
    Account,
)
from eth_utils import (
    int_to_big_endian,
)
from eth_account.messages import (
    encode_intended_validator,
)
from eth_abi.packed import (
    encode_abi_packed,
)


def sign_score(key, params):
    types = ['bytes32', 'address', 'uint256']
    values = [
        params['game_id'],
        params['user'],
        params['score'],
    ]
    encoded_values = encode_abi_packed(types, values)
    message = encode_intended_validator(
        validator_address=params['contract'],
        primitive=encoded_values,
    )
    signed = Account.sign_message(message, key)
    vrs = (
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
    )
    return vrs
