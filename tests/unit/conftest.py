import pytest
import json
from eth_utils import (
    pad_left,
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


num_accounts = 3
accounts = []
for i in range(1, num_accounts + 1):
    pk_bytes = pad_left(int_to_big_endian(i), 32, b'\x00')
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


def _compile(filepath, contract_name, allow_paths=None):
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
def compile():
    return _compile
