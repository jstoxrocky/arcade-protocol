import pytest
import json
from eth_utils import (
    int_to_big_endian,
)
from web3 import (
    Web3,
    Account,
)
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
import os
from contracts import (
    BIN_DIR,
)


num_accounts = 3
accounts = []
for i in range(1, num_accounts + 1):
    pk_bytes = int_to_big_endian(i).rjust(32, b'\x00')
    account = Account.from_key(pk_bytes)
    accounts.append(account)


@pytest.fixture(scope="module")
def web3():
    provider = EthereumTesterProvider()
    return Web3(provider)


@pytest.fixture(scope="module")
def owner(web3):
    account = accounts[0]
    assert web3.eth.getBalance(account.address) > 0
    return account


@pytest.fixture(scope="module")
def user(web3):
    account = accounts[1]
    assert web3.eth.getBalance(account.address) > 0
    return account


@pytest.fixture(scope="module")
def user2(web3):
    account = accounts[2]
    assert web3.eth.getBalance(account.address) > 0
    return account


def compile():
    filepath = os.path.join(BIN_DIR, "combined.json")
    with open(filepath) as f:
        compiled_artifacts = json.load(f)

    data = compiled_artifacts["contracts"]["solidity/Arcade.sol:Arcade"]
    abi = data["abi"]
    bytecode = data["bin"]
    bytecode_runtime = data["bin-runtime"]

    return abi, bytecode, bytecode_runtime


@pytest.fixture(scope="module")
def Contract(web3):
    abi, code, code_runtime = compile()
    return web3.eth.contract(
        abi=abi,
        bytecode=code,
        bytecode_runtime=code_runtime,
    )


@pytest.fixture(scope="function")
def contract(web3, Contract, owner):
    deploy_txn = Contract.constructor().transact({'from': owner.address})
    deploy_receipt = web3.eth.waitForTransactionReceipt(deploy_txn)
    assert deploy_receipt is not None
    contract = Contract(address=deploy_receipt['contractAddress'])
    assert owner.address == contract.functions.owner().call()
    return contract
