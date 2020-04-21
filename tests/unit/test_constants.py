GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
PRICE = 100000000000000  # 0.0001 ETH
PAYMENT_CODE = '0x64e604787cbf194841e7b68d7cd28786f6c9a0a3ab9f8b0a0e87cb4387ab0107'  # noqa: E501
PERCENT_FEE = 10


def test_initial_game_price(contract):
    expected_price = 0
    price = contract.get_price(GAME_ID)
    assert price == expected_price


def test_initial_payment_code(contract, user):
    expected_payment_code = '0x0000000000000000000000000000000000000000000000000000000000000000'  # noqa: E501
    payment_code = contract.get_payment_code(GAME_ID, user.address)
    assert payment_code == expected_payment_code


def test_initial_highscore(contract):
    expected_highscore = 0
    highscore = contract.get_highscore(GAME_ID)
    assert highscore == expected_highscore


def test_initial_jackpot(contract):
    expected_jackpot = 0
    jackpot = contract.get_jackpot(GAME_ID)
    assert jackpot == expected_jackpot


def test_initial_game_owner(contract):
    expected_owner = '0x0000000000000000000000000000000000000000'
    owner = contract.get_owner(GAME_ID)
    assert owner == expected_owner


def test_initial_percent_fee(contract):
    expected_percent_fee = 0
    percent_fee = contract.get_percent_fee(GAME_ID)
    assert percent_fee == expected_percent_fee


def test_game_price(contract, owner):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    expected_price = PRICE
    actual_price = contract.get_price(GAME_ID)
    assert actual_price == expected_price


def test_game_owner(contract, owner):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    expected_owner = owner.address
    owner = contract.get_owner(GAME_ID)
    assert owner == expected_owner


def test_percent_fee(contract, owner):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    expected_percent_fee = PERCENT_FEE
    percent_fee = contract.get_percent_fee(GAME_ID)
    assert percent_fee == expected_percent_fee
