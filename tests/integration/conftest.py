import pytest
import os
import json
from web3.providers import (
    HTTPProvider,
)
from web3 import (
    Web3,
)


ARCADE_ABI = '[{"constant": true, "inputs": [], "name": "round", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "jackpot", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "highscore", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": true, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "payable": false, "stateMutability": "view", "type": "function"}, {"constant": false, "inputs": [{"name": "h", "type": "bytes32"}, {"name": "v", "type": "uint8"}, {"name": "r", "type": "bytes32"}, {"name": "s", "type": "bytes32"}, {"name": "_addr", "type": "address"}, {"name": "score", "type": "uint256"}], "name": "uploadScore", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor"}]'  # noqa: E501
ARCADE_ADDRESS = os.environ['ARCADE_ADDRESS']


@pytest.fixture(scope="module")
def web3():
    infura_token = os.environ['INFURA_ACCESS_TOKEN']
    provider = HTTPProvider('https://rinkeby.infura.io/%s' % (infura_token))
    return Web3(provider)


@pytest.fixture(scope="function")
def arcade_contract(web3):
    contract = web3.eth.contract(
        abi=json.loads(ARCADE_ABI),
        address=ARCADE_ADDRESS,
    )
    return contract
