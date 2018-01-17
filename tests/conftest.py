import pytest
import os
import json
from web3.contract import (
    ConciseContract,
)
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from solc import (
    compile_files,
)
from zero_x_2048_contracts import (
    CONTRACTS_DIR,
)


def compile(filepath, contract_name, allow_paths=None):
    compilation = compile_files(
        [filepath],
        allow_paths=allow_paths,
    )
    compilation = compilation[filepath+":"+contract_name]
    abi = json.dumps(compilation['abi'])
    bytecode = compilation['bin']
    bytecode_runtime = compilation['bin-runtime']
    return abi, bytecode, bytecode_runtime


@pytest.fixture(scope="module")
def Contract(web3):
    filepath = os.path.join(CONTRACTS_DIR, "Eth0x2048.sol")
    contract_name = 'Eth0x2048'
    abi, code, code_runtime = compile(filepath, contract_name)
    return web3.eth.contract(
        abi=abi,
        bytecode=code,
        bytecode_runtime=code_runtime,
    )


@pytest.fixture(scope="function")
def contract(web3, Contract, owner):
    deploy_txn = Contract.deploy({'from': owner})
    deploy_receipt = wait_for_transaction_receipt(web3, deploy_txn)
    assert deploy_receipt is not None
    _contract = Contract(address=deploy_receipt['contractAddress'])
    concise_contract = ConciseContract(_contract)
    assert owner == concise_contract.owner()
    return concise_contract


@pytest.fixture(scope="function")
def user_has_paid(contract, user):
    if not contract.getParticipation(user):
        price = contract.price()
        contract.pay(transact={'from': user, 'value': price})
    assert contract.getParticipation(user)
