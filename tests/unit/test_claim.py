from scripts.sign import (
    sign_score,
)
from hexbytes import (
    HexBytes,
)


GAME_ID = '0x240e634ba82fa510c7e25243cc95d456bb1b6c11ef8c695ddd555eb5cd443f74'
PRICE = 100000000000000  # 0.0001 ETH
SCORE = 1


def test_jackpot(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    expected_jackpot = 0
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    jackpot = contract.get_jackpot(GAME_ID)
    assert jackpot == expected_jackpot


def test_user_balance(web3, contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    jackpot = contract.get_jackpot(GAME_ID)
    expected_balance = web3.eth.getBalance(user.address) + jackpot
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    gas_cost = receipt['gasPrice'] * receipt['gasUsed']
    balance = web3.eth.getBalance(user.address) + gas_cost  # Adjust for gas
    assert balance == expected_balance


def test_contract_balance(web3, contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    jackpot = contract.get_jackpot(GAME_ID)
    expected_balance = web3.eth.getBalance(contract.address) - jackpot
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 1
    balance = web3.eth.getBalance(contract.address)
    assert balance == expected_balance


def test_signer_is_not_owner(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(user.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_user_is_not_signed_user(contract, owner, user, user2):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user2.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_uploads_wrong_score(web3, contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    bad_score = SCORE + 1
    receipt = contract.claim(GAME_ID, bad_score, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_score_too_low(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    low_score = 0
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': low_score,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, low_score, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_game_id_doesnt_match_arcade_signer(contract, owner, user):
    contract.add_game(GAME_ID, PRICE, from_addr=owner)

    wrong_game_id = '0xf7ba25e4cb13d1cac1dffb5044ac9001438eb1251b07a484fbe3428bc825099b'  # noqa: E501
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(wrong_game_id, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0


def test_game_doesnt_exist(contract, owner, user):
    params = {
        'game_id': HexBytes(GAME_ID),
        'user': user.address,
        'score': SCORE,
        'contract': contract.address,
    }
    vrs = sign_score(owner.key, params)
    receipt = contract.claim(GAME_ID, SCORE, vrs, from_addr=user)
    assert receipt['status'] == 0
