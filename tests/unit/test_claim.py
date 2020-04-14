import pytest
from web3._utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from contracts import (
    sign_score,
)
from eth_utils import (
    int_to_big_endian,
)
from eth_utils import (
    keccak,
)


def add_game(web3, contract, from_address, game_id, price):
    txhash = contract.functions.addGame(
        game_id,
        price,
    ).transact({'from': from_address})
    txn_receipt = wait_for_transaction_receipt(
        web3,
        txhash,
        timeout=120,
        poll_latency=0.1
    )
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def claim(web3, signed, contract, from_address, score, game_id):
    txhash = contract.functions.claim(
        game_id,
        score,
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
    ).transact({'from': from_address})
    txn_receipt = wait_for_transaction_receipt(
        web3,
        txhash,
        timeout=120,
        poll_latency=0.1
    )
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_jackpot(web3, contract, owner, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    expected_output = 0
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    claim(web3, signed, contract, user.address, score, game_id)
    output = contract.functions.getJackpot(game_id).call()

    assert output == expected_output


def test_user_balance(web3, contract, owner, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    jackpot = contract.functions.getJackpot(game_id).call()
    expected_output = web3.eth.getBalance(user.address) + jackpot
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    gas_cost = claim(
        web3,
        signed,
        contract,
        user.address,
        score,
        game_id,
    )
    output = web3.eth.getBalance(user.address) + gas_cost  # Adjust for gas

    # Test
    assert output == expected_output


def test_contract_balance(web3, contract, owner, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    jackpot = contract.functions.getJackpot(game_id).call()
    expected_output = web3.eth.getBalance(contract.address) - jackpot
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    claim(web3, signed, contract, user.address, score, game_id)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_output


def test_signer_is_not_owner(web3, contract, owner, user2, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    score = 1
    signed = sign_score(
        user2.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(web3, signed, contract, user.address, score, game_id)


def test_user_is_not_signed_user(web3, contract, owner, user, user2):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    game_id = keccak(text='ABC')
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user2.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(web3, signed, contract, user.address, score, game_id)


def test_uploads_wrong_score(web3, contract, owner, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    score = 1
    wrong_score = 100
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(
            web3,
            signed,
            contract,
            user.address,
            wrong_score,
            game_id,
        )


def test_score_too_low(web3, contract, owner, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, owner.address, game_id, price)

    game_id = keccak(text='ABC')
    score = 0
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(web3, signed, contract, user.address, score, game_id)


def test_game_id_doesnt_match_arcade_signer(web3, contract, owner, user):
    game_id = keccak(text='ABC')
    wrong_game_id = keccak(text='DEF')
    price = 100000000000000  # 0.0001 ETH
    add_game(web3, contract, owner.address, wrong_game_id, price)

    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(
            web3,
            signed,
            contract,
            user.address,
            score,
            wrong_game_id,
        )


def test_game_doesnt_exist(web3, contract, owner, user):
    game_id = keccak(text='ABC')
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        claim(web3, signed, contract, user.address, score, game_id)
