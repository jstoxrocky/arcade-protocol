import pytest
import os
import json
from web3.providers import (
    HTTPProvider,
)
from web3 import (
    Web3,
    Account,
)
from eth_utils import (
    to_wei,
)


ABI = '[{"constant": true, "inputs": [{"name": "", "type": "uint256"}, {"name": "", "type": "address"}], "name": "participants", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "round", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [], "name": "pay", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function"}, {"constant": true, "inputs": [], "name": "percentFee", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "jackpot", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "price", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "h", "type": "bytes32"}, {"name": "v", "type": "uint8"}, {"name": "r", "type": "bytes32"}, {"name": "s", "type": "bytes32"}, {"name": "_addr", "type": "address"}, {"name": "score", "type": "uint256"}], "name": "uploadScore", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"constant": true, "inputs": [{"name": "_addr", "type": "address"}], "name": "getParticipation", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "h", "type": "bytes32"}, {"name": "v", "type": "uint8"}, {"name": "r", "type": "bytes32"}, {"name": "s", "type": "bytes32"}, {"name": "_addr", "type": "address"}, {"name": "_price", "type": "uint256"}], "name": "adjustPrice", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor"}]'  # noqa: E501
ADDRESS = '0x8848c724B853307083F44526ad32C039b5ee1451'


@pytest.fixture(scope="module")
def rinkeby_address():
    return ADDRESS


@pytest.fixture(scope="module")
def web3():
    infura_token = os.environ['INFURA_ACCESS_TOKEN']
    provider = HTTPProvider('https://rinkeby.infura.io/%s' % (infura_token))
    return Web3(provider)


@pytest.fixture(scope="function")
def contract(web3):
    contract = web3.eth.contract(
        abi=json.loads(ABI),
        address=ADDRESS,
    )
    return contract


@pytest.fixture(scope="module")
def owner(web3):
    privkey = os.environ['ARCADE_PRIVATE_KEY']
    owner = Account.privateKeyToAccount(privkey)
    return owner


@pytest.fixture(scope="module")
def user(web3):
    privkey = os.environ['RINKEBY_USER']
    user = Account.privateKeyToAccount(privkey)
    assert web3.eth.getBalance(user.address) >= to_wei(1, 'ether')
    return user
