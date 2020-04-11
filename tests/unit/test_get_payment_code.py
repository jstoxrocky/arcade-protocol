from eth_utils import (
    keccak,
)


def test_initial_payment_code(web3, contract, user):
    """
    It should be equal to zero
    """
    game_id = keccak(text='ABC')
    expected_output = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    output = contract.functions.getPaymentCode(game_id, user.address).call()
    assert output == expected_output
