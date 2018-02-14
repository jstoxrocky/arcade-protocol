import pytest
import requests
from web3 import (
    Account,
)
from eth_utils import (
    decode_hex,
)
from contracts import (
    sign,
)
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)


BASE_URL = 'https://www.0x2048-int.net'


def test_contract_has_address(contract, rinkeby_address):
    assert contract.address == rinkeby_address


def test_contract_has_code(web3, contract):
    assert web3.eth.getCode(contract.address) != b''


def test_contract_owner_is_from_envvar(web3, contract, owner):
    contract_owner = contract.functions.owner().call()
    assert contract_owner == owner.address


def test_signer_is_contract_owner(web3, contract, user):
    data = dict(user=user.address)
    result = requests.get(BASE_URL + '/price', params=data)
    data_from_endpoint = result.json()
    signed = data_from_endpoint['signature']
    signer = Account.recover(
        signed['messageHash'],
        signature=signed['signature'],
    )
    contract_owner = contract.functions.owner().call()
    assert contract_owner == signer


def test_contract_address_same_as_webserver(web3, contract, owner, user):
    # Since all owner tests pass, and we have price, user
    # If this test fails, then it is the contract address
    data = dict(user=user.address)
    result = requests.get(BASE_URL + '/price', params=data)
    data_from_endpoint = result.json()
    price = data_from_endpoint['price']
    signed = data_from_endpoint['signature']
    self_signed = sign(owner.privateKey, contract.address, user.address, price)
    assert signed['signature'] == self_signed['signature']


@pytest.mark.skip
def test_price(web3, contract, user):
    data = dict(user=user.address)
    result = requests.get(BASE_URL + '/price', params=data)
    data_from_endpoint = result.json()
    price = data_from_endpoint['price']
    signed = data_from_endpoint['signature']

    tx = contract.functions.adjustPrice(
        signed['messageHash'],
        signed['v'],
        decode_hex(signed['r']),
        decode_hex(signed['s']),
        user.address,
        price,
    ).buildTransaction({
        'from': user.address,
        'gas': 4000000,
        'gasPrice': 2000000000,
        'nonce': web3.eth.getTransactionCount(user.address),
    })
    signed_tx = Account.signTransaction(tx, user.privateKey)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = wait_for_transaction_receipt(web3, tx_hash)
    assert receipt is not None
    assert bool(receipt.status)
    assert contract.functions.price().call() == price
