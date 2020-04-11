from eth_utils import (
    keccak,
)


def test_contract_initial_highscore(web3, contract):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_output = 0
    output = contract.functions.getHighscore(game_id).call()
    assert output == expected_output


def test_contract_initial_jackpot(web3, contract):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_output = 0
    output = contract.functions.getJackpot(game_id).call()
    assert output == expected_output


def test_contract_owner(web3, contract, owner):
    """
    It should be equal to the test owner address
    """
    expected_output = owner.address
    output = contract.functions.owner().call()
    assert output == expected_output


def test_contract_price(web3, contract, owner, user):
    """
    It should be equal to 1000000000000000 (0.001 ETH)
    """
    expected_output = 100000000000000
    output = contract.functions.price().call()
    assert output == expected_output
