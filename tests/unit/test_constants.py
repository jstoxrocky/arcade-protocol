from eth_utils import (
    keccak,
)
from hexbytes import (
    HexBytes,
)
from web3._utils.transactions import (
    wait_for_transaction_receipt,
)


def test_initial_game_price(web3, contract):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_price = 0
    price = contract.functions.getPrice(game_id).call()
    assert price == expected_price


def test_initial_payment_code(web3, contract, user):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_payment_code = '0x0000000000000000000000000000000000000000000000000000000000000000'  # noqa: E501
    payment_code = contract.functions.getPaymentCode(
        game_id,
        user.address,
    ).call()
    assert HexBytes(payment_code).hex() == expected_payment_code


def test_initial_highscore(web3, contract):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_highscore = 0
    highscore = contract.functions.getHighscore(game_id).call()
    assert highscore == expected_highscore


def test_initial_jackpot(web3, contract):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_jackpot = 0
    jackpot = contract.functions.getJackpot(game_id).call()
    assert jackpot == expected_jackpot


def test_initial_game_owner(web3, contract, user):
    """
    It should be equal to the test owner address
    """
    game_id = keccak(text='ABC')
    expected_owner = '0x0000000000000000000000000000000000000000'
    owner = contract.functions.getOwner(game_id).call()
    assert owner == expected_owner


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


def test_game_price(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)

    expected_price = price
    actual_price = contract.functions.getPrice(game_id).call()
    assert actual_price == expected_price


def test_game_owner(web3, contract, user):
    price = 100000000000000  # 0.0001 ETH
    game_id = keccak(text='ABC')
    add_game(web3, contract, user.address, game_id, price)

    expected_owner = user.address
    owner = contract.functions.getOwner(game_id).call()
    assert owner == expected_owner
