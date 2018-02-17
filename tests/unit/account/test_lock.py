from web3.utils.transactions import (
    wait_for_transaction_receipt,
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


def test_user_arcade_balance(web3, contract, user):
    value = 17
    expected_user_arcade_balance = value
    lock(web3, contract, user, value)
    user_arcade_balance = contract.functions.balanceOf(user.address).call()
    assert user_arcade_balance == expected_user_arcade_balance


def test_contract_balance(web3, contract, user):
    contract_balance = web3.eth.getBalance(contract.address)
    value = 17
    expected_contract_balance = contract_balance + value
    lock(web3, contract, user, value)
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance


def test_user_balance(web3, contract, user):
    user_balance = web3.eth.getBalance(user.address)
    value = 17
    expected_user_balance = user_balance - value
    gas_cost = lock(web3, contract, user, value)
    user_balance = web3.eth.getBalance(user.address)
    assert user_balance == expected_user_balance - gas_cost
