from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from web3 import (
    Web3,
)


def to_32byte_hex(val):
    return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))


def transferToOwner(web3, contract, owner, user, value):
    msg = Web3.soliditySha3(
        ['address', 'address', 'uint256'],
        [contract.address, user.address, value]
    )
    signed = user.sign(msg)
    txhash = contract.functions.transferToOwner(
        signed['messageHash'],
        signed['v'],
        to_32byte_hex(signed['r']),
        to_32byte_hex(signed['s']),
        user.address,
        value,
    ).transact({
        'from': owner.address,
    })
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    tx = web3.eth.getTransaction(txhash)
    gas_cost = tx['gasPrice'] * txn_receipt['gasUsed']
    return gas_cost


def test_user_arcade_balance(web3, contract, owner, desposited_user):
    # Expected
    user = desposited_user
    user_arcade_balance = contract.functions.balanceOf(user.address).call()
    value = 7
    expected_user_arcade_balance = user_arcade_balance - value

    # Run
    transferToOwner(web3, contract, owner, user, value)

    # Test
    user_arcade_balance = contract.functions.balanceOf(user.address).call()
    assert user_arcade_balance == expected_user_arcade_balance


def test_contract_balance(web3, contract, owner, desposited_user):
    # Expected
    user = desposited_user
    contract_balance = web3.eth.getBalance(contract.address)
    value = 7
    expected_contract_balance = contract_balance - value

    # Run
    transferToOwner(web3, contract, owner, user, value)

    # Test
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance


def test_function_caller_balance(web3, contract, owner, desposited_user):
    # Expected
    user = desposited_user
    owner_balance = web3.eth.getBalance(owner.address)
    value = 7
    expected_owner_balance = owner_balance + value

    # Run
    gas_cost = transferToOwner(web3, contract, owner, user, value)

    # Test
    owner_balance = web3.eth.getBalance(owner.address)
    assert owner_balance == expected_owner_balance - gas_cost
