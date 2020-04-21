import click
import os
import json
from web3 import (
    Web3,
    Account,
)
from web3.providers import (
    HTTPProvider,
)
from contract_interactor import (
    ContractInteractor,
)


@click.command()
@click.argument('method')
@click.option('--address', default=None)
@click.option('--game_id', default=None)
def run(method, address, game_id):
    # Web3
    INFURA_PROJECT_ID = os.environ['INFURA_PROJECT_ID']
    INFURA_PROJECT_SECRET = os.environ['INFURA_PROJECT_SECRET']
    headers = {"auth": ("", INFURA_PROJECT_SECRET)}
    uri = 'https://ropsten.infura.io/v3/%s' % (INFURA_PROJECT_ID)
    web3 = Web3(HTTPProvider(uri, headers))

    # Owner
    owner = Account.from_key(os.environ['PRIVATE_KEY_0x2048'])

    # ABI
    filepath = 'bin/combined.json'
    with open(filepath) as f:
        compiled_artifacts = json.load(f)
    data = compiled_artifacts["contracts"]
    contract_data = data["solidity/ArcadeProtocol.sol:ArcadeProtocol"]
    abi = contract_data["abi"]
    bytecode = contract_data["bin"]

    # Run
    interactor = ContractInteractor(web3)
    if method == 'deploy':
        interactor.deploy(abi, bytecode, from_addr=owner)
    elif method == 'add_game':
        price = 100000000000000  # 0.0001 ETH
        fee = 1
        interactor.set_contract(abi, address)
        interactor.add_game(game_id, price, fee, from_addr=owner)


if __name__ == '__main__':
    run()
