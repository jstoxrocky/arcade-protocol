import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from contracts import (
    hash_data,
    sign,
)
from eth_utils import (
    int_to_big_endian,
)


def upload_score(web3, contract, user, signed, score):
    txhash = contract.uploadScore(
        signed['msgHash'],
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
        user,
        score,
        transact={'from': user})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_round(web3, contract, owner_priv, user, user_has_paid):
    # Formulate expected output
    expected_ouput = contract.round() + 1

    # Generate actual output
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    upload_score(web3, contract, user, signed, score)
    output = contract.round()

    # Test
    assert output == expected_ouput


def test_jackpot(web3, contract, owner_priv, user, user_has_paid):
    # Formulate expected output
    expected_ouput = 0

    # Generate actual output
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    upload_score(web3, contract, user, signed, score)
    output = contract.jackpot()

    # Test
    assert output == expected_ouput


def test_participation(web3, contract, owner_priv, user, user_has_paid):
    # Formulate expected output
    expected_ouput = False

    # Generate actual output
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    upload_score(web3, contract, user, signed, score)
    output = contract.getParticipation(user)

    # Test
    assert output == expected_ouput


def test_user_balance(web3, contract, owner_priv, user, user_has_paid):
    # Formulate expected output
    jackpot = contract.jackpot()
    expected_ouput = web3.eth.getBalance(user) + jackpot

    # Generate actual output
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    gas_cost = upload_score(web3, contract, user, signed, score)
    output = web3.eth.getBalance(user) + gas_cost  # Adjust for gas

    # Test
    assert output == expected_ouput


def test_contract_balance(web3, contract, owner_priv, user, user_has_paid):
    # Formulate expected output
    jackpot = contract.jackpot()
    expected_ouput = web3.eth.getBalance(contract.address) - jackpot

    # Generate actual output
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    upload_score(web3, contract, user, signed, score)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_ouput


def test_signer_is_not_owner(web3, contract, _owner_priv, user, user_has_paid):
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, _owner_priv)
    with pytest.raises(TransactionFailed):
        upload_score(web3, contract, user, signed, score)


def test_uploads_wrong_score(web3, contract, owner_priv, user, user_has_paid):
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    with pytest.raises(TransactionFailed):
        new_score = score + 1
        upload_score(web3, contract, user, signed, new_score)


def test_score_too_low(web3, contract, owner_priv, user, user_has_paid):
    score = 0
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    with pytest.raises(TransactionFailed):
        upload_score(web3, contract, user, signed, score)


def test_has_not_paid(web3, contract, owner_priv, user):
    score = 1
    msg_hash = hash_data(contract.address, user, score)
    signed = sign(msg_hash, owner_priv)
    with pytest.raises(TransactionFailed):
        upload_score(web3, contract, user, signed, score)
