import os
import json


this = os.path.dirname(__file__)
tests = os.path.join(this, '..')
base = os.path.abspath(os.path.join(tests, '..'))
integration_tests_json = os.path.join(base, 'integration-json-fixtures')
constants_dir = os.path.join(integration_tests_json, 'constants')


def test_contract_has_code(web3, arcade_contract):
    contract = arcade_contract
    assert web3.eth.getCode(contract.address) != b''


def test_contract_owner_matches_integration_json(arcade_contract):
    contract = arcade_contract
    contract_owner = contract.functions.owner().call()
    filepath = os.path.join(constants_dir, "address.json")
    with open(filepath) as f:
        data = json.load(f)
    assert data['owner'] == contract_owner


def test_contract_address_matches_integration_json(arcade_contract):
    contract = arcade_contract
    filepath = os.path.join(constants_dir, "address.json")
    with open(filepath) as f:
        data = json.load(f)
    assert data['arcade'] == contract.address


def test_contract_abi_matches_integration_json(arcade_contract):
    contract = arcade_contract
    filepath = os.path.join(constants_dir, "abi.json")
    with open(filepath) as f:
        data = json.load(f)
    assert data['arcade'] == contract.abi
