from arcade_protocol.crypto import (
    sign_score,
)


PAYMENT_CODE = '0x64e604787cbf194841e7b68d7cd28786f6c9a0a3ab9f8b0a0e87cb4387ab0107'  # noqa: E501
PRICE = 100000000000000  # 0.0001 ETH
SCORE = 1
PERCENT_FEE = 10


def test_jackpot(contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    expected_jackpot = 0
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    jackpot = contract.get_jackpot()
    assert jackpot == expected_jackpot


def test_user_balance(web3, contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)

    initial_balance = web3.eth.getBalance(user.address)
    jackpot = contract.get_jackpot()
    fee = jackpot * PERCENT_FEE // 100
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    gas_cost = receipt['gasPrice'] * receipt['gasUsed']
    expected_balance = initial_balance + jackpot - gas_cost - fee
    balance = web3.eth.getBalance(user.address)
    assert balance == expected_balance


def test_contract_balance(web3, contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)

    jackpot = contract.get_jackpot()
    expected_balance = web3.eth.getBalance(contract.address) - jackpot
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    balance = web3.eth.getBalance(contract.address)
    assert balance == expected_balance


def test_owner_gets_paid_fee(web3, contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)

    jackpot = contract.get_jackpot()
    fee = jackpot * PERCENT_FEE // 100
    expected_balance = web3.eth.getBalance(owner.address) + fee
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    balance = web3.eth.getBalance(owner.address)
    assert balance == expected_balance


def test_signer_is_not_owner(contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    key = user.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_user_is_not_signed_user(contract, owner, user, user2):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user2.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_uploads_wrong_score(web3, contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    bad_score = SCORE + 1
    receipt = contract.claim_highscore(bad_score, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_score_too_low(contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    low_score = 0
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, low_score)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(low_score, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_game_id_doesnt_match_arcade_signer(contract, owner, user):
    contract.add_game(PRICE, PERCENT_FEE, from_addr=owner)
    contract.pay(PAYMENT_CODE, value=PRICE, from_addr=user)
    wrong_game_id = '0xf7ba25e4cb13d1cac1dffb5044ac9001438eb1251b07a484fbe3428bc825099b'  # noqa: E501
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    contract.game_id = wrong_game_id
    receipt = contract.claim_highscore(
        SCORE,
        vrs,
        from_addr=user,
    )
    assert receipt['status'] == 0


def test_game_doesnt_exist(contract, owner, user):
    key = owner.key
    address = contract.address
    game_id = contract.game_id
    sig = sign_score(key, address, game_id, user.address, SCORE)
    vrs = (sig['v'], sig['r'], sig['s'])
    receipt = contract.claim_highscore(SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0
