from web3 import (
    Account,
)
from toolz.dicttoolz import (
    valmap,
)
from eth_account.messages import (
    encode_structured_data,
)
from eth_utils import (
    int_to_big_endian,
)


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
            {"name": "score", "type": "uint256"},
            {"name": "gameId", "type": "bytes32"}
        ],
    },
    "primaryType": "Highscore",
    "domain": {
        "name": "0x2048",
        "version": "1.0",
        "chainId": 1,
    },
}


def sign_score(private_key, params):
    structured_highscore["message"] = {
        "user": params['user'],
        "score": params['score'],
        "gameId": params['game_id'],
    }
    structured_highscore["domain"]["verifyingContract"] = params['contract']
    structured_msg = encode_structured_data(
        primitive=structured_highscore,
    )
    # sign_message passes data through
    # eth_account.messages._hash_eip191_message which is keccak256
    signed = Account.sign_message(structured_msg, private_key)
    signed = valmap(lambda x: x.hex() if isinstance(x, bytes) else x, signed)
    vrs = (
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
    )
    return vrs
