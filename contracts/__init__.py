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
from web3._utils.encoding import (
    hex_encode_abi_type,
)
from eth_utils import (
    add_0x_prefix,
    remove_0x_prefix,
)
from eth_typing import (
    HexStr,
)


_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'solidity')
BIN_DIR = os.path.join(_outer_dir_abs, 'bin')


def sign(private_key, contract, user, *values):
    # This should be a function
    abi_types = ['address', 'uint256']
    values = [user, values[0]]
    message = add_0x_prefix(HexStr(''.join(
        remove_0x_prefix(hex_encode_abi_type(abi_type, value))
        for abi_type, value
        in zip(abi_types, values)
    )))
    eip191_message = encode_intended_validator(
        validator_address=contract,
        hexstr=message,
    )
    # sign_message passes data through
    # eth_account.messages._hash_eip191_message
    signed = Account.sign_message(eip191_message, private_key)
    signed = valmap(lambda x: x.hex() if isinstance(x, bytes) else x, signed)
    return signed
