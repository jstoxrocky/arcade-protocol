import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)


def pay(web3, contract, user, price):
    txhash = contract.functions.pay().transact({'from': user, 'value': price})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_jackpot(web3, contract, user):
    # Formulate expected output
    initial_value = contract.functions.jackpot().call()
    price = contract.functions.price().call()
    percent_fee = contract.functions.percentFee().call()
    to_jackpot = int(price * (1 - (percent_fee / 100)))
    expected_output = initial_value + to_jackpot

    # Generate actual output
    pay(web3, contract, user.address, price)
    output = contract.functions.jackpot().call()

    # Test
    assert output == expected_output


def test_participation(web3, contract, user):
    # Formulate expected output
    expected_ouput = True

    # Generate actual output
    price = contract.functions.price().call()
    pay(web3, contract, user.address, price)
    output = contract.functions.getParticipation(user.address).call()

    # Test
    assert output == expected_ouput


def test_user_balance(web3, contract, user):
    # Formulate expected output
    price = contract.functions.price().call()
    expected_ouput = web3.eth.getBalance(user.address) - price

    # Generate actual output
    gas_cost = pay(web3, contract, user.address, price)
    output = web3.eth.getBalance(user.address) + gas_cost  # Adjust for gas

    # Test
    assert output == expected_ouput


def test_owner_balance(web3, contract, owner, user):
    # Formulate expected output
    price = contract.functions.price().call()
    percent_fee = contract.functions.percentFee().call()
    to_owner = int(price * (percent_fee / 100))
    expected_ouput = web3.eth.getBalance(owner.address) + to_owner
    # Generate actual output
    pay(web3, contract, user.address, price)
    output = web3.eth.getBalance(owner.address)
    # Test
    assert output == expected_ouput


def test_contract_balance(web3, contract, user):
    # Formulate expected output
    price = contract.functions.price().call()
    percent_fee = contract.functions.percentFee().call()
    to_jackpot = int(price * (1 - (percent_fee / 100)))
    expected_ouput = web3.eth.getBalance(contract.address) + to_jackpot

    # Generate actual output
    pay(web3, contract, user.address, price)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_ouput


def test_price_too_low(web3, contract, user):
    price = contract.functions.price().call() - 1
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user.address, price)


def test_already_paid(web3, contract, user, user_has_paid):
    price = contract.functions.price().call()
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user.address, price)
