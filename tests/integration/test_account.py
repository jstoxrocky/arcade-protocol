import pytest
import os
import json


this = os.path.dirname(__file__)
tests = os.path.join(this, '..')
base = os.path.abspath(os.path.join(tests, '..'))
integration_tests_json = os.path.join(base, 'integration-tests-json')
constants_dir = os.path.join(integration_tests_json, 'constants')


@pytest.mark.skip
def test_contract_has_code(web3, account_contract):
    contract = account_contract
    assert web3.eth.getCode(contract.address) != b''


@pytest.mark.skip
def test_contract_owner_matches_integration_json(account_contract):
    contract = account_contract
    contract_owner = contract.functions.owner().call()
    filepath = os.path.join(constants_dir, "address.json")
    with open(filepath) as f:
        data = json.load(f)
    assert data['owner'] == contract_owner


def test_contract_address_matches_integration_json(account_contract):
    contract = account_contract
    filepath = os.path.join(constants_dir, "address.json")
    with open(filepath) as f:
        data = json.load(f)
    assert data['account'] == contract.address
