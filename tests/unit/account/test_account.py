from web3.utils.transactions import (
    wait_for_transaction_receipt,
)


def test_lock(web3, contract, user):
    balance = 1
    timeout = 2
    txhash = contract.functions.lock(_timeout=timeout).transact({
        'from': user.address,
        'value': balance,
    })
    txn_receipt = wait_for_transaction_receipt(web3, txhash)
    assert txn_receipt is not None
    balance = contract.functions.balanceOf(user.address).call()
    timeout = contract.functions.timeoutOf(user.address).call()
    assert balance == balance
    assert timeout == timeout
