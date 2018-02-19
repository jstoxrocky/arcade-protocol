import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from contracts import (
    sign,
)
from eth_utils import (
    int_to_big_endian,
)


def upload_score(web3, signed, contract, user, score):
    txhash = contract.functions.uploadScore(
        signed['messageHash'],
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
        user,
        score,
    ).transact({'from': user})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_jackpot(web3, contract, owner, user):
    # Formulate expected output
    expected_ouput = 0

    # Generate actual output
    score = 1
    signed = sign(owner.privateKey, contract.address, user.address, score)
    upload_score(web3, signed, contract, user.address, score)
    output = contract.functions.jackpot().call()

    # Test
    assert output == expected_ouput


def test_round(web3, contract, owner, user):
    # Formulate expected output
    expected_ouput = contract.functions.round().call() + 1

    # Generate actual output
    score = 1
    signed = sign(owner.privateKey, contract.address, user.address, score)
    upload_score(web3, signed, contract, user.address, score)
    output = contract.functions.round().call()

    # Test
    assert output == expected_ouput


def test_user_balance(web3, contract, owner, user):
    # Formulate expected output
    jackpot = contract.functions.jackpot().call()
    expected_ouput = web3.eth.getBalance(user.address) + jackpot

    # Generate actual output
    score = 1
    signed = sign(owner.privateKey, contract.address, user.address, score)
    gas_cost = upload_score(web3, signed, contract, user.address, score)
    output = web3.eth.getBalance(user.address) + gas_cost  # Adjust for gas

    # Test
    assert output == expected_ouput


def test_contract_balance(web3, contract, owner, user):
    # Formulate expected output
    jackpot = contract.functions.jackpot().call()
    expected_ouput = web3.eth.getBalance(contract.address) - jackpot

    # Generate actual output
    score = 1
    signed = sign(owner.privateKey, contract.address, user.address, score)
    upload_score(web3, signed, contract, user.address, score)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_ouput


def test_signer_is_not_owner(web3, contract, user2, user):
    score = 1
    signed = sign(user2.privateKey, contract.address, user.address, score)
    with pytest.raises(TransactionFailed):
        upload_score(web3, signed, contract, user.address, score)


def test_uploads_wrong_score(web3, contract, owner, user):
    score = 1
    wrong_score = 100
    signed = sign(owner.privateKey, contract.address, user.address, score)
    with pytest.raises(TransactionFailed):
        upload_score(web3, signed, contract, user.address, wrong_score)


def test_score_too_low(web3, contract, owner, user):
    score = 0
    signed = sign(owner.privateKey, contract.address, user.address, score)
    with pytest.raises(TransactionFailed):
        upload_score(web3, signed, contract, user.address, score)
