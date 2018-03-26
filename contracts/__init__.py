import os
from web3 import (
    Web3,
    Account,
)
from toolz.dicttoolz import (
    valmap,
)


_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'solidity')


def sign(private_key, contract, user, *values):
    abi_types = ['address', 'address'] + ['uint256'] * len(values)
    msg = Web3.soliditySha3(abi_types, [contract, user] + list(values))
    signed = Account.sign(msg, private_key)
    signed = valmap(lambda x: x.hex() if isinstance(x, bytes) else x, signed)
    return signed
