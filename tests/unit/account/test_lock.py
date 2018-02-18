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


def unlock(web3, contract, user):
    txhash = contract.functions.unlock().transact({'from': user.address})
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
    lock(web3, contract, user, value)
    balance = contract.functions.balanceOf(user.address).call()
    assert balance == expected_balance


def test_contract_balance(web3, contract, user):
    """
    It should add 17 ETH to the contracts's Ethereum wallet
    """
    balance = web3.eth.getBalance(contract.address)
    value = to_wei(17, 'ether')
    expected_balance = balance + value
    lock(web3, contract, user, value)
    balance = web3.eth.getBalance(contract.address)
    assert balance == expected_balance


def test_user_balance(web3, contract, user):
    """
    It should withdraw 17 ETH from the user's Ethereum wallet (and gas costs)
    """
    balance = web3.eth.getBalance(user.address)
    value = to_wei(17, 'ether')
    expected_balance = balance - value
    gas_cost = lock(web3, contract, user, value)
    balance = web3.eth.getBalance(user.address)
    assert balance == expected_balance - gas_cost


def test_timeout(web3, contract, user):
    """
    It should add a timeout to the user's arcade account
    of block_timeout blocks
    """
    value = to_wei(17, 'ether')
    block_timeout = contract.functions.blockTimeout().call()
    expected_timeout = web3.eth.blockNumber + block_timeout
    lock(web3, contract, user, value)
    timeout = contract.functions.timeoutOf(user.address).call()
    # Add one since eth-tester increments a block on transaction
    assert timeout == expected_timeout + 1


def test_unlock_before_timeout(web3, contract, EthereumTester, user):
    """
    It should not allow a user to unlock funds in their arcade account
    before the timeout is up
    """
    value = to_wei(17, 'ether')
    lock(web3, contract, user, value)
    with pytest.raises(TransactionFailed):
        unlock(web3, contract, user)


def test_unlock_user_arcade_balance(web3, contract, EthereumTester, user):
    """
    It should subtract all ETH from a user's arcade account
    """
    value = to_wei(17, 'ether')
    # Lock and mine
    lock(web3, contract, user, value)
    # Mine blocks
    # The unlock function requires that MORE than
    # block_timeout blocks has elapsed
    # We would need to mine block_timeout + 1 blocks
    # but the lock function mines
    # one block when called so this is not necessary
    block_timeout = contract.functions.blockTimeout().call()
    EthereumTester.mine_blocks(num_blocks=block_timeout, coinbase=None)

    expected_balance = 0
    unlock(web3, contract, user)
    balance = contract.functions.balanceOf(user.address).call()
    assert balance == expected_balance


def test_unlock_user_balance(web3, contract, EthereumTester, user):
    """
    It should increase the user's Ethereum wallet by the balance amount
    """
    # Lock and mine
    value = to_wei(17, 'ether')
    lock(web3, contract, user, value)
    block_timeout = contract.functions.blockTimeout().call()
    EthereumTester.mine_blocks(num_blocks=block_timeout, coinbase=None)

    wallet_balance = web3.eth.getBalance(user.address)
    arcade_balance = contract.functions.balanceOf(user.address).call()
    expected_wallet_balance = wallet_balance + arcade_balance

    unlock_gas_cost = unlock(web3, contract, user)
    wallet_balance = web3.eth.getBalance(user.address)
    assert wallet_balance == expected_wallet_balance - unlock_gas_cost


def test_unlock_contract_balance(web3, contract, EthereumTester, user):
    """
    It should decrease the contract's Ethereum wallet by the balance amount
    """
    # Lock and mine
    value = to_wei(17, 'ether')
    lock(web3, contract, user, value)
    block_timeout = contract.functions.blockTimeout().call()
    EthereumTester.mine_blocks(num_blocks=block_timeout, coinbase=None)

    contract_balance = web3.eth.getBalance(contract.address)
    arcade_balance = contract.functions.balanceOf(user.address).call()
    expected_contract_balance = contract_balance - arcade_balance

    unlock(web3, contract, user)
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance
