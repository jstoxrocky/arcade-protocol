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


def adjust_price(web3, signed, contract, user, price):
    txhash = contract.functions.adjustPrice(
        signed['messageHash'],
        signed['v'],
        int_to_big_endian(signed['r']),
        int_to_big_endian(signed['s']),
        user,
        price,
    ).transact({'from': user})
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_price(web3, contract, owner, user):
    # Formulate expected output
    increment = 1
    price = contract.functions.price().call()
    expected_ouput = price + increment

    # Generate actual output
    price = price + increment
    signed = sign(owner.privateKey, contract.address, user.address, price)
    adjust_price(web3, signed, contract, user.address, price)
    output = contract.functions.price().call()

    # Test
    assert output == expected_ouput


def test_signer_is_not_owner(web3, contract, _owner, user):
    price = contract.functions.price().call()
    signed = sign(_owner.privateKey, contract.address, user.address, price)
    with pytest.raises(TransactionFailed):
        adjust_price(web3, signed, contract, user.address, price)


def test_adjusts_wrong_price(web3, contract, owner, user):
    price = contract.functions.price().call()
    signed = sign(owner.privateKey, contract.address, user.address, price)
    with pytest.raises(TransactionFailed):
        price = 0
        adjust_price(web3, signed, contract, user.address, price)
