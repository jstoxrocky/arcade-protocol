import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)


def pay(web3, contract, user, price):
    txhash = contract.transact({'from': user, 'value': price}).pay()
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_jackpot(web3, contract, user):
    # Formulate expected output
    initial_value = contract.call({'from': user}).jackpot()
    price = contract.call({'from': user}).price()
    percent_fee = contract.call({'from': user}).percentFee()
    to_jackpot = int(price * (1 - (percent_fee / 100)))
    expected_output = initial_value + to_jackpot

    # Generate actual output
    pay(web3, contract, user, price)
    output = contract.call({'from': user}).jackpot()

    # Test
    assert output == expected_output


def test_participation(web3, contract, user):
    # Formulate expected output
    expected_ouput = True

    # Generate actual output
    price = contract.call({'from': user}).price()
    pay(web3, contract, user, price)
    output = contract.call({'from': user}).getParticipation(user)

    # Test
    assert output == expected_ouput


def test_user_balance(web3, contract, user):
    # Formulate expected output
    price = contract.call({'from': user}).price()
    expected_ouput = web3.eth.getBalance(user) - price

    # Generate actual output
    gas_cost = pay(web3, contract, user, price)
    output = web3.eth.getBalance(user) + gas_cost  # Adjust for gas

    # Test
    assert output == expected_ouput


def test_owner_balance(web3, contract, owner, user):
    # Formulate expected output
    price = contract.call({'from': user}).price()
    percent_fee = contract.call({'from': user}).percentFee()
    to_owner = int(price * (percent_fee / 100))
    expected_ouput = web3.eth.getBalance(owner) + to_owner
    # Generate actual output
    pay(web3, contract, user, price)
    output = web3.eth.getBalance(owner)
    # Test
    assert output == expected_ouput


def test_contract_balance(web3, contract, user):
    # Formulate expected output
    price = contract.call({'from': user}).price()
    percent_fee = contract.call({'from': user}).percentFee()
    to_jackpot = int(price * (1 - (percent_fee / 100)))
    expected_ouput = web3.eth.getBalance(contract.address) + to_jackpot

    # Generate actual output
    pay(web3, contract, user, price)
    output = web3.eth.getBalance(contract.address)

    # Test
    assert output == expected_ouput


def test_price_too_low(web3, contract, user):
    price = contract.call({'from': user}).price() - 1
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user, price)


def test_already_paid(web3, contract, user, user_has_paid):
    price = contract.call({'from': user}).price()
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user, price)
