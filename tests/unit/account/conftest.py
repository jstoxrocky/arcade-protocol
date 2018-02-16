import pytest
import os
from web3.utils.transactions import (
    wait_for_transaction_receipt,
)
from contracts import (
    CONTRACTS_DIR,
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


@pytest.fixture(scope="function")
def contract(web3, Contract, owner):
    deploy_txn = Contract.deploy({'from': owner.address})
    deploy_receipt = wait_for_transaction_receipt(web3, deploy_txn)
    assert deploy_receipt is not None
    contract = Contract(address=deploy_receipt['contractAddress'])
    assert owner.address == contract.functions.owner().call()
    return contract


@pytest.fixture(scope="function")
def user_has_paid(contract, user):
    if not contract.functions.getParticipation(user.address).call():
        price = contract.functions.price().call()
        contract.functions.pay().transact({
            'from': user.address,
            'value': price,
        })
    assert contract.functions.getParticipation(user.address).call()
