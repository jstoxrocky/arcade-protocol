from arcade_protocol.crypto import (
    sign_score,
    random_32bytes,
)
from web3 import (
    Account,
)
from eth_account.messages import (
    encode_intended_validator,
)
from hexbytes import (
    HexBytes,
)
from eth_abi.packed import (
    encode_abi_packed,
)


CONTRACT = '0x2c35B443d3a15588c4dfCE0da2C8Af0264ed22bb'
GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
SCORE = 1


def test_sign_score(user, owner, monkeypatch):
    expected_signer = owner.address
    vrs = sign_score(owner.key, CONTRACT, GAME_ID, user.address, SCORE)
    types = ['bytes32', 'address', 'uint256']
    values = [
        HexBytes(GAME_ID),
        user.address,
        SCORE,
    ]
    encoded_values = encode_abi_packed(types, values)
    message = encode_intended_validator(
        validator_address=CONTRACT,
        primitive=encoded_values,
    )
    actual_signer = Account.recover_message(
        message,
        vrs=vrs,
    )

    assert actual_signer == expected_signer


def test_generate_random_32bytes():
    value = HexBytes(random_32bytes())
    assert len(value) == 32
