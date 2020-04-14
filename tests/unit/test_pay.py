import pytest
from web3._utils.transactions import (
    wait_for_transaction_receipt,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils import (
    keccak,
)


def add_game(web3, contract, from_address, game_id, price):
    txhash = contract.functions.addGame(
        game_id,
        price,
    ).transact({'from': from_address})
    txn_receipt = wait_for_transaction_receipt(
        web3,
        txhash,
        timeout=120,
        poll_latency=0.1
    )
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def pay(web3, contract, user, price, game_id, payment_code):
    txhash = contract.functions.pay(
        game_id,
        payment_code,
    ).transact({'from': user, 'value': price})
    txn_receipt = wait_for_transaction_receipt(
        web3,
        txhash,
        timeout=120,
        poll_latency=0.1
    )
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_pay_success(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)

    payment_code = keccak(text='123')
    price = contract.functions.getPrice(game_id).call()
    jackpot = contract.functions.getJackpot(game_id).call()
    expected_payment_code = payment_code
    exected_jackpot = jackpot + price

    pay(web3, contract, user.address, price, game_id, payment_code)
    output_jackpot = contract.functions.getJackpot(game_id).call()
    output_payment_code = contract.functions.getPaymentCode(
        game_id,
        user.address,
    ).call()

    assert output_payment_code == expected_payment_code
    assert output_jackpot == exected_jackpot


def test_pay_incorrect_price(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)

    payment_code = keccak(text='123')
    price = contract.functions.getPrice(game_id).call() - 1
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user.address, price, game_id, payment_code)


def test_pay_game_does_not_exist(web3, contract, user):
    game_id = keccak(text='ABC')

    payment_code = keccak(text='123')
    price = 0
    with pytest.raises(TransactionFailed):
        pay(web3, contract, user.address, price, game_id, payment_code)
