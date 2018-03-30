def test_initial_nonce(web3, contract, user):
    """
    It should be equal to zero
    """
    expected_output = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    output = contract.functions.getNonce(user.address).call()
    assert output == expected_output
