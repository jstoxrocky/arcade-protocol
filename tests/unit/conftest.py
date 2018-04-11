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
from solc import (
    compile_files,
)
import os
from contracts import (
    CONTRACTS_DIR,
)


num_accounts = 3
accounts = []
for i in range(1, num_accounts + 1):
    pk_bytes = int_to_big_endian(i).rjust(32, b'\x00')
    account = Account.privateKeyToAccount(pk_bytes)
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


def compile(filepath, contract_name, allow_paths=None):
    compilation = compile_files(
        [filepath],
        allow_paths=allow_paths,
    )
    compilation = compilation[filepath + ":" + contract_name]
    abi = json.dumps(compilation['abi'])
    bytecode = compilation['bin']
    bytecode_runtime = compilation['bin-runtime']
    return abi, bytecode, bytecode_runtime


@pytest.fixture(scope="module")
def Contract(web3):
    filepath = os.path.join(CONTRACTS_DIR, "Arcade.sol")
    contract_name = 'Arcade'
    abi, code, code_runtime = compile(filepath, contract_name)
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
