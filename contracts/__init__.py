import os
from web3 import (
    Account,
)
from toolz.dicttoolz import (
    valmap,
)
from eth_account.messages import (
    encode_structured_data,
)


_inner_file = os.path.dirname(__file__)
_outer_dir_rel = os.path.join(_inner_file, '..')
_outer_dir_abs = os.path.abspath(_outer_dir_rel)
CONTRACTS_DIR = os.path.join(_outer_dir_abs, 'solidity')
BIN_DIR = os.path.join(_outer_dir_abs, 'bin')


structured_highscore = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"}
        ],
        "Highscore": [
            {"name": "user", "type": "address"},
            {"name": "score", "type": "uint256"}
        ],
    },
    "primaryType": "Highscore",
    "domain": {
        "name": "0x2048",
        "version": "1",
        "chainId": 1,
    },
}


def sign_score(private_key, contract, user, score):
    structured_highscore["message"] = {
        "user": user,
        "score": score,
    }
    structured_highscore["domain"]["verifyingContract"] = contract
    structured_msg = encode_structured_data(
        primitive=structured_highscore,
    )
    # sign_message passes data through
    # eth_account.messages._hash_eip191_message which is keccak256
    signed = Account.sign_message(structured_msg, private_key)
    signed = valmap(lambda x: x.hex() if isinstance(x, bytes) else x, signed)
    return signed
