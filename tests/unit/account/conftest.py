import pytest
import os
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from contracts import (
    CONTRACTS_DIR,
)
from eth_utils import (
    to_wei,
)


@pytest.fixture(scope="module")
def Contract(web3, compile):
    filepath = os.path.join(CONTRACTS_DIR, "Account.sol")
    contract_name = 'Account'
    abi, code, code_runtime = compile(filepath, contract_name)
    return web3.eth.contract(
        abi=abi,
        bytecode=code,
        bytecode_runtime=code_runtime,
    )


@pytest.fixture(scope="module")
def contract(web3, Contract, owner):
    deploy_txn = Contract.deploy({'from': owner.address})
    deploy_receipt = wait_for_transaction_receipt(web3, deploy_txn)
    assert deploy_receipt is not None
    contract = Contract(address=deploy_receipt['contractAddress'])
    assert owner.address == contract.functions.owner().call()
    return contract


@pytest.fixture(scope="module", autouse=True)
def desposited_user(web3, contract, user2):
    value = to_wei(21, 'ether')
    txhash = contract.functions.deposit().transact({
        'from': user2.address,
        'value': value,
    })
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    return user2


@pytest.fixture(scope="module")
def EthereumTester(web3):
    provider, = web3.providers
    return provider.ethereum_tester
