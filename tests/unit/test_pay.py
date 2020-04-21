GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
PRICE = 100000000000000  # 0.0001 ETH
PAYMENT_CODE = '0x64e604787cbf194841e7b68d7cd28786f6c9a0a3ab9f8b0a0e87cb4387ab0107'  # noqa: E501
PERCENT_FEE = 10


def test_pay_success(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)

    initial_jackpot = contract.get_jackpot(GAME_ID)
    expected_payment_code = PAYMENT_CODE
    expected_jackpot = initial_jackpot + PRICE

    receipt = contract.pay(GAME_ID, PAYMENT_CODE, value=PRICE, from_addr=user)
    assert receipt['status'] == 1
    jackpot = contract.get_jackpot(GAME_ID)
    payment_code = contract.get_payment_code(GAME_ID, user.address)
    assert payment_code == expected_payment_code
    assert jackpot == expected_jackpot


def test_pay_bad_price(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, PERCENT_FEE, from_addr=owner)
    bad_price = PRICE - 1
    receipt = contract.pay(
        GAME_ID,
        PAYMENT_CODE,
        value=bad_price,
        from_addr=user,
    )
    assert receipt['status'] == 0


def test_pay_game_does_not_exist(contract, user):
    price = 0  # Non-existant game has zero price
    receipt = contract.pay(GAME_ID, PAYMENT_CODE, value=price, from_addr=user)
    assert receipt['status'] == 0
