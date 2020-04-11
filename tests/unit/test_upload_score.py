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


def upload_score(web3, signed, contract, user, score, game_id):
    txhash = contract.functions.uploadScore(
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
        score,
        game_id,
    ).transact({'from': user})
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
    game_id = keccak(text='ABC')
    expected_output = 0
    score = 1
    signed = sign_score(
        owner.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    upload_score(web3, signed, contract, user.address, score, game_id)
    output = contract.functions.getJackpot(game_id).call()

    assert output == expected_output


def test_user_balance(web3, contract, owner, user):
    game_id = keccak(text='ABC')
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
    gas_cost = upload_score(
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
    game_id = keccak(text='ABC')
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
    upload_score(web3, signed, contract, user.address, score, game_id)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_output


def test_signer_is_not_owner(web3, contract, user2, user):
    game_id = keccak(text='ABC')
    score = 1
    signed = sign_score(
        user2.key,
        contract.address,
        user.address,
        score,
        game_id,
    )
    with pytest.raises(TransactionFailed):
        upload_score(web3, signed, contract, user.address, score, game_id)


def test_user_is_not_signed_user(web3, contract, owner, user, user2):
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
        upload_score(web3, signed, contract, user.address, score, game_id)


def test_uploads_wrong_score(web3, contract, owner, user):
    game_id = keccak(text='ABC')
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
        upload_score(
            web3,
            signed,
            contract,
            user.address,
            wrong_score,
            game_id,
        )


def test_score_too_low(web3, contract, owner, user):
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
        upload_score(web3, signed, contract, user.address, score, game_id)


def test_game_id_doesnt_match_arcade_signer(web3, contract, owner, user):
    attempt_at_winning_another_game_id = keccak(text='DEF')
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
        upload_score(
            web3,
            signed,
            contract,
            user.address,
            score,
            attempt_at_winning_another_game_id,
        )
