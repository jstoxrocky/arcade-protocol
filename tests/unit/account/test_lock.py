import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_utils import (
    to_wei,
)
from eth_tester.exceptions import (
    TransactionFailed,
)


def lock(web3, contract, user, value):
    txhash = contract.functions.lock().transact({
        'from': user.address,
        'value': value,
    })
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_user_arcade_balance(web3, function_specific_contract, user):
    contract = function_specific_contract
    value = to_wei(17, 'ether')
    expected_user_arcade_balance = value
    lock(web3, contract, user, value)
    user_arcade_balance = contract.functions.balanceOf(user.address).call()
    assert user_arcade_balance == expected_user_arcade_balance


def test_contract_balance(web3, function_specific_contract, user):
    contract = function_specific_contract
    contract_balance = web3.eth.getBalance(contract.address)
    value = to_wei(17, 'ether')
    expected_contract_balance = contract_balance + value
    lock(web3, contract, user, value)
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance


def test_user_balance(web3, function_specific_contract, user):
    contract = function_specific_contract
    user_balance = web3.eth.getBalance(user.address)
    value = to_wei(17, 'ether')
    expected_user_balance = user_balance - value
    gas_cost = lock(web3, contract, user, value)
    user_balance = web3.eth.getBalance(user.address)
    assert user_balance == expected_user_balance - gas_cost


def test_timeout(web3, function_specific_contract, user):
    contract = function_specific_contract
    value = to_wei(17, 'ether')
    expected_timeout = web3.eth.blockNumber + 5
    lock(web3, contract, user, value)
    timeout = contract.functions.timeoutOf(user.address).call()
    # Add one since eth-tester increments a block on transaction
    assert timeout == expected_timeout + 1


def test_user_cannot_lock_twice(web3, function_specific_contract, user):
    contract = function_specific_contract
    value = to_wei(17, 'ether')
    lock(web3, contract, user, value)
    with pytest.raises(TransactionFailed):
        lock(web3, contract, user, value)
