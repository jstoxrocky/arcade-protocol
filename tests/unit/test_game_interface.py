from arcade_protocol.game_interface import (
    GameInterface,
)
from eth_utils import (
    keccak,
)
from hexbytes import (
    HexBytes,
)


GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
CONTRACT = '0x2c35B443d3a15588c4dfCE0da2C8Af0264ed22bb'
PERCENT_FEE = 10
PAYMENT_CODE = '0x64e604787cbf194841e7b68d7cd28786f6c9a0a3ab9f8b0a0e87cb4387ab0107'  # noqa: E501
SCORE = 1
PRICE = 100000000000000  # 0.0001 ETH


def test_new_payment_code(mocker):
    random_value = '0x1234'
    mocker.patch(
        'arcade_protocol.game_interface.random_32bytes',
    ).return_value = random_value
    expected_payment_code = random_value
    payment_code = GameInterface.new_payment_code()
    assert payment_code == expected_payment_code


def test_confirm_payment_success(contract, user, owner):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(GAME_ID, PAYMENT_CODE, value=PRICE, from_addr=user)
    arcade = GameInterface(contract, GAME_ID, player=user.address)
    error = arcade.confirm_payment(
        PAYMENT_CODE,
    )
    assert error is False


def test_confirm_payment_user_hasnt_uploaded_payment_code(
    contract,
    user,
    owner,
):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    old_payment_code = HexBytes(keccak(text='XYZ')).hex()
    contract.pay(GAME_ID, old_payment_code, value=PRICE, from_addr=user)
    arcade = GameInterface(contract, GAME_ID, player=user.address)
    error = arcade.confirm_payment(
        PAYMENT_CODE,
    )
    assert error is True
