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
from eth_utils import (
    encode_hex,
    add_0x_prefix,
)
from web3._utils.abi import (
    get_constructor_abi,
    merge_args_and_kwargs,
)
from web3._utils.contracts import (
    encode_abi,
)
from web3._utils.transactions import (
    wait_for_transaction_receipt,
)


@click.command()
@click.argument('filepath')
@click.argument('contract_name')
@click.argument('owner_envvar')
@click.option('--chainid', default=4, help='chain to deploy to')
@click.option('--force',
              prompt='Are you sure you want to deploy? y/n',
              help='confirmation')
def run(filepath, contract_name, owner_envvar, chainid, force):
    if force != 'y':
        click.echo('aborting deployment')
        return
    click.echo('...deploying %s to chainid %s' % (filepath, chainid))
    abi, bytecode, bytecode_runtime = compile(filepath)
    web3 = get_provider()
    deployment_data = create_deployement_data(web3, abi, bytecode)
    owner = Account.from_key(os.environ[owner_envvar])
    tx = create_transaction(web3, owner, deployment_data)
    signed_tx = Account.signTransaction(tx, owner.key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    click.echo('transaction hash: %s' % (encode_hex(tx_hash)))
    deploy_receipt = wait_for_transaction_receipt(
        web3,
        tx_hash,
        timeout=120,
        poll_latency=5.0
    )
    click.echo(deploy_receipt)


def compile(filepath):
    with open(filepath) as f:
        compiled_artifacts = json.load(f)

    data = compiled_artifacts["contracts"]["solidity/Arcade.sol:Arcade"]
    abi = data["abi"]
    bytecode = data["bin"]
    bytecode_runtime = data["bin-runtime"]

    return abi, bytecode, bytecode_runtime


def get_provider():
    INFURA_PROJECT_ID = os.environ['INFURA_PROJECT_ID']
    INFURA_PROJECT_SECRET = os.environ['INFURA_PROJECT_SECRET']
    headers = {"auth": ("", INFURA_PROJECT_SECRET)}
    uri = 'https://ropsten.infura.io/v3/%s' % (INFURA_PROJECT_ID)
    web3 = Web3(HTTPProvider(uri, headers))
    return web3


def create_deployement_data(web3, abi, bytecode):
    constructor_abi = get_constructor_abi(json.loads(abi))
    args = ()
    kwargs = {}
    arguments = merge_args_and_kwargs(constructor_abi, args, kwargs)
    deployment_data = add_0x_prefix(
        encode_abi(web3, constructor_abi, arguments, data=bytecode)
    )
    return deployment_data


def create_transaction(web3, owner, deployment_data):
    # eth gas station fast price in gwei 01/10/20202
    recommended_gas_price_gwei = 8
    recommended_gas_price = Web3.toWei(recommended_gas_price_gwei, 'gwei')
    tx = {
        'gas': 3000000,
        'gasPrice': recommended_gas_price,
        'nonce': web3.eth.getTransactionCount(owner.address),
        'data': deployment_data,
        'chainId': None,
        'to': '',
    }
    return tx


if __name__ == '__main__':
    run()
