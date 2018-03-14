from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from web3 import (
    Web3,
)
from eth_keys import (
    keys,
)
from eth_account.signing import (
    to_eth_v,
)


DISCLAIMER = 'This signature is for intended for use with 0x2048 at the below Rinkeby address. If you are seeing this message and not interacting with 0x2048, someone may be attempting forge your signature'  # noqa: E501
ACCOUNT_ADDRESS = '0x8848c724b853307083f44526aD32c039B5eE1452'


def raw_sign(msg_hash, private_key):
    key = keys.PrivateKey(private_key)
    raw_signature = key.sign_msg_hash(msg_hash)
    return raw_signature


def hash_typed_data(msg_params):
    data = list(map(lambda x: x['value'], msg_params))
    types = list(map(lambda x: x['type'], msg_params))
    schema = list(map(lambda x: ' '.join([x['type'], x['name']]), msg_params))
    schema_hash = Web3.soliditySha3(['string'] * len(msg_params), schema)
    data_hash = Web3.soliditySha3(types, data)
    msg_hash = Web3.soliditySha3(
        ['bytes32', 'bytes32'],
        [schema_hash, data_hash],
    )
    return msg_hash


def sign_typed_data(msg_params, private_key):
    msg_hash = hash_typed_data(msg_params)
    key = keys.PrivateKey(private_key)
    raw_signature = key.sign_msg_hash(msg_hash)
    v_raw, r, s = raw_signature.vrs
    v = to_eth_v(v_raw)
    return v, r, s


def to_32byte_hex(val):
    return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))


def finalizeIOU(web3, contract, owner, user, nonce):
    msg_params = [
        {'type': 'address', 'name': DISCLAIMER, 'value': contract.address},
        {'type': 'address', 'name': 'user', 'value': user.address},
        {'type': 'uint256', 'name': 'nonce', 'value': nonce},
    ]
    schema = list(map(lambda x: ' '.join([x['type'], x['name']]), msg_params))
    schema_hash = Web3.soliditySha3(['string'] * len(msg_params), schema)
    v, r, s = sign_typed_data(msg_params, user.privateKey)
    txhash = contract.functions.finalizeIOU(
        v,
        to_32byte_hex(r),
        to_32byte_hex(s),
        schema_hash,
        user.address,
        nonce,
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
    nonce = contract.functions.getNonce(user.address).call() + 1
    price = contract.functions.price().call()
    expected_user_arcade_balance = user_arcade_balance - price

    # Run
    finalizeIOU(web3, contract, owner, user, nonce)

    # Test
    user_arcade_balance = contract.functions.balanceOf(user.address).call()
    assert user_arcade_balance == expected_user_arcade_balance


def test_contract_balance(web3, contract, owner, desposited_user):
    # Expected
    user = desposited_user
    contract_balance = web3.eth.getBalance(contract.address)
    nonce = contract.functions.getNonce(user.address).call() + 1
    price = contract.functions.price().call()
    expected_contract_balance = contract_balance - price

    # Run
    finalizeIOU(web3, contract, owner, user, nonce)

    # Test
    contract_balance = web3.eth.getBalance(contract.address)
    assert contract_balance == expected_contract_balance


def test_function_caller_balance(web3, contract, owner, desposited_user):
    # Expected
    user = desposited_user
    owner_balance = web3.eth.getBalance(owner.address)
    nonce = contract.functions.getNonce(user.address).call() + 1
    price = contract.functions.price().call()
    expected_owner_balance = owner_balance + price

    # Run
    gas_cost = finalizeIOU(web3, contract, owner, user, nonce)

    # Test
    owner_balance = web3.eth.getBalance(owner.address)
    assert owner_balance == expected_owner_balance - gas_cost
