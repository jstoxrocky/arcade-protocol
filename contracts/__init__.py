import os
from web3 import (
    Account,
)
from toolz.dicttoolz import (
    valmap,
)
from eth_account.messages import (
    encode_intended_validator,
)
from eth_abi.packed import (
    encode_abi_packed,
)


_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'solidity')
BIN_DIR = os.path.join(_outer_dir_abs, 'bin')


def sign_score(private_key, contract, user, score):
    abi_types = ['address', 'uint256']
    values = [user, score]
    message = encode_abi_packed(abi_types, values)
    eip191_message = encode_intended_validator(
        validator_address=contract,
        primitive=message,
    )
    # sign_message passes data through
    # eth_account.messages._hash_eip191_message which is keccak256
    signed = Account.sign_message(eip191_message, private_key)
    signed = valmap(lambda x: x.hex() if isinstance(x, bytes) else x, signed)
    return signed
