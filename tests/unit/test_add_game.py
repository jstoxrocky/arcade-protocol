import pytest
from web3.exceptions import (
    ValidationError,
)


PRICE = 100000000000000  # 0.0001 ETH
PERCENT_FEE = 10


def test_add_game_success(contract, owner):
    receipt = contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    assert receipt['status'] == 1


def test_game_id_already_taken(contract, owner):
    receipt = contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    assert receipt['status'] == 1
    receipt = contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    assert receipt['status'] == 0


def test_free_game(contract, owner):
    price = 0
    receipt = contract.add_game(price, PERCENT_FEE, from_addr=owner)
    assert receipt['status'] == 0


def test_percent_fee_over_100(contract, owner):
    receipt = contract.add_game(PRICE, 101, from_addr=owner)
    assert receipt['status'] == 0


def test_percent_fee_negative(contract, owner):
    with pytest.raises(ValidationError):
        contract.add_game(PRICE, -1, from_addr=owner)
