import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils import (
    keccak,
)


def pay(web3, contract, user, price, nonce):
    txhash = contract.functions.pay(
        nonce,
    ).transact({'from': user, 'value': price})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_pay_success(web3, contract, user):
    """
    It should succeed with a jackpot increased by `price` and an updated nonce
    """
    nonce = keccak(b'')
    price = contract.functions.price().call()
    jackpot = contract.functions.jackpot().call()
    expected_nonce = nonce
    exected_jackpot = jackpot + price

    pay(web3, contract, user.address, price, nonce)
    output_jackpot = contract.functions.jackpot().call()
    output_nonce = contract.functions.getNonce(user.address).call()

    assert output_nonce == expected_nonce
    assert output_jackpot == exected_jackpot


def test_pay_incorrect_price(web3, contract, user):
    """
    It should fail
    """
    nonce = keccak(b'')
    price = price = contract.functions.price().call() - 1
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user.address, price, nonce)
