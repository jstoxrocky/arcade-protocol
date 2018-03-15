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


def deposit(web3, contract, user, value):
    txhash = contract.functions.deposit().transact({
        'from': user.address,
        'value': value,
    })
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def withdraw(web3, contract, user):
    txhash = contract.functions.withdraw().transact({'from': user.address})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_user_arcade_balance(web3, contract, user):
    """
    It should add 17 ETH to the user's arcade account
    """
    value = to_wei(17, 'ether')
    expected_balance = value
    deposit(web3, contract, user, value)
    balance = contract.functions.balanceOf(user.address).call()
    assert balance == expected_balance


def test_contract_balance(web3, contract, user):
    """
    It should add 17 ETH to the contracts's Ethereum wallet
    """
    balance = web3.eth.getBalance(contract.address)
    value = to_wei(17, 'ether')
    expected_balance = balance + value
    deposit(web3, contract, user, value)
    balance = web3.eth.getBalance(contract.address)
    assert balance == expected_balance


def test_user_balance(web3, contract, user):
    """
    It should withdraw 17 ETH from the user's Ethereum wallet (and gas costs)
    """
    balance = web3.eth.getBalance(user.address)
    value = to_wei(17, 'ether')
    expected_balance = balance - value
    gas_cost = deposit(web3, contract, user, value)
    balance = web3.eth.getBalance(user.address)
    assert balance == expected_balance - gas_cost


def test_timeout(web3, contract, user):
    """
    It should add a timeout to the user's arcade account
    of bdeposit_timeout seconds
    """
    value = to_wei(17, 'ether')
    deposit(web3, contract, user, value)

    block_timeout = contract.functions.blockTimeout().call()
    current_block = web3.eth.getBlock('latest')
    timestamp = current_block.timestamp
    expected_timeout = timestamp + block_timeout

    timeout = contract.functions.timeoutOf(user.address).call()
    assert timeout == expected_timeout


def test_withdraw_before_timeout(web3, contract, user):
    """
    It should not allow a user to withdraw funds in their arcade account
    before the timeout is up
    """
    value = to_wei(17, 'ether')
    deposit(web3, contract, user, value)
    with pytest.raises(TransactionFailed):
        withdraw(web3, contract, user)


def test_withdraw_user_arcade_balance(web3, contract, EthereumTester, user):
    """
    It should subtract all ETH from a user's arcade account
    """
    value = to_wei(17, 'ether')
    # deposit and mine
    deposit(web3, contract, user, value)
    block_timeout = contract.functions.blockTimeout().call()
    current_block = web3.eth.getBlock('latest')
    timestamp = current_block.timestamp
    # +1 since inequality is strictly greater than
    EthereumTester.time_travel(timestamp + block_timeout + 1)

    expected_balance = 0
    withdraw(web3, contract, user)
    balance = contract.functions.balanceOf(user.address).call()
    assert balance == expected_balance


def test_withdraw_user_balance(web3, contract, EthereumTester, user):
    """
    It should increase the user's Ethereum wallet by the balance amount
    """
    # deposit and mine
    value = to_wei(17, 'ether')
    deposit(web3, contract, user, value)
    block_timeout = contract.functions.blockTimeout().call()
    current_block = web3.eth.getBlock('latest')
    timestamp = current_block.timestamp
    # +1 since inequality is strictly greater than
    EthereumTester.time_travel(timestamp + block_timeout + 1)

    wallet_balance = web3.eth.getBalance(user.address)
    arcade_balance = contract.functions.balanceOf(user.address).call()
    expected_wallet_balance = wallet_balance + arcade_balance

    withdraw_gas_cost = withdraw(web3, contract, user)
    wallet_balance = web3.eth.getBalance(user.address)
    assert wallet_balance == expected_wallet_balance - withdraw_gas_cost


def test_withdraw_contract_balance(web3, contract, EthereumTester, user):
    """
    It should decrease the contract's Ethereum wallet by the balance amount
    """
    # deposit and mine
    value = to_wei(17, 'ether')
    deposit(web3, contract, user, value)
    block_timeout = contract.functions.blockTimeout().call()
    current_block = web3.eth.getBlock('latest')
    timestamp = current_block.timestamp
    # +1 since inequality is strictly greater than
    EthereumTester.time_travel(timestamp + block_timeout + 1)

    contract_balance = web3.eth.getBalance(contract.address)
    arcade_balance = contract.functions.balanceOf(user.address).call()
    expected_contract_balance = contract_balance - arcade_balance

    withdraw(web3, contract, user)
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance
