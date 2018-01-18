import pytest
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils import (
    int_to_big_endian,
)
from contracts import (
    hash_data,
    sign,
)


def adjust_price(web3, contract, user, signed, score):
    txhash = contract.adjustPrice(
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


def test_price(web3, contract, owner_priv, user):
    # Formulate expected output
    increment = 1
    price = contract.price()
    expected_ouput = price + increment

    # Generate actual output
    price = price + increment
    msg_hash = hash_data(contract.address, user, price)
    signed = sign(msg_hash, owner_priv)
    adjust_price(web3, contract, user, signed, price)
    output = contract.price()

    # Test
    assert output == expected_ouput


def test_signer_is_not_owner(web3, contract, _owner_priv, user):
    price = contract.price()
    msg_hash = hash_data(contract.address, user, price)
    signed = sign(msg_hash, _owner_priv)
    with pytest.raises(TransactionFailed):
        adjust_price(web3, contract, user, signed, price)


def test_adjusts_wrong_price(web3, contract, owner_priv, user):
    price = contract.price()
    msg_hash = hash_data(contract.address, user, price)
    signed = sign(msg_hash, owner_priv)
    with pytest.raises(TransactionFailed):
        price = 0
        adjust_price(web3, contract, user, signed, price)
