import os
import web3
from eth_utils import (
    keccak,
    decode_hex,
    int_to_big_endian,
    pad_left,
)


_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'contracts')


def int_to_uint(value, uint=256):
    return pad_left(int_to_big_endian(value), int(2*(uint**0.5)), '\x00')


def hex_to_address(value):
    return decode_hex(value)


def hash_data(contract, user, value):
    _contract = hex_to_address(contract)
    _user = hex_to_address(user)
    _value = int_to_uint(value)
    _bytes = b"".join([_contract, _user, _value])
    msg_hash = keccak(_bytes)
    return msg_hash


def sign(message, private_key):
    signed = web3.account.Account.sign(message, private_key)
    return {
        'msg': signed['message'].hex(),
        'msgHash': signed['messageHash'].hex(),
        'v': signed['v'],
        'r': signed['r'],
        's': signed['s'],
        'signature': signed['signature'].hex(),
    }
