from eth_utils import (
    keccak,
)
from web3._utils.transactions import (
    wait_for_transaction_receipt,
)
import pytest
from eth_tester.exceptions import (
    TransactionFailed,
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


def test_add_game_success(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)


def test_game_id_already_taken(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)
    with pytest.raises(TransactionFailed):
        add_game(web3, contract, user.address, game_id, price)


def test_free_game(web3, contract, user):
    price = 0
    game_id = keccak(text='ABC')
    with pytest.raises(TransactionFailed):
        add_game(web3, contract, user.address, game_id, price)
