import pytest
import json
from web3 import (
    Web3,
    Account,
)
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from eth_utils import (
    int_to_big_endian,
)
from scripts.contract_interactor import (
    ContractInteractor,
)


# The ten default accounts added are the ones with
# private keys equal to the first 10 digits. If this ever changes
# just do this:
# provider = EthereumTesterProvider()
# t = provider.ethereum_tester
# t.add_account(private_key)
def int_to_test_account(i):
    pk_bytes = int_to_big_endian(i).rjust(32, b'\x00')
    account = Account.from_key(pk_bytes)
    return account


@pytest.fixture(scope="module")
def owner():
    account = int_to_test_account(1)
    return account


@pytest.fixture(scope="module")
def user():
    account = int_to_test_account(2)
    return account


@pytest.fixture(scope="module")
def user2():
    account = int_to_test_account(3)
    return account


@pytest.fixture(scope="module")
def web3(owner):
    # Web3
    provider = EthereumTesterProvider()
    web3 = Web3(provider)
    return web3


@pytest.fixture(scope="function")
def contract(web3, owner):
    # ABI
    filepath = 'bin/combined.json'
    with open(filepath) as f:
        compiled_artifacts = json.load(f)
    data = compiled_artifacts["contracts"]["solidity/Arcade.sol:Arcade"]
    abi = data["abi"]
    bytecode = data["bin"]

    interactor = ContractInteractor(web3)
    receipt = interactor.deploy(abi, bytecode, from_addr=owner)
    address = receipt['contractAddress']
    interactor.set_contract(abi, address)
    return interactor
