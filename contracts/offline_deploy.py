import click
import os
import json
from solc import (
    compile_files,
)
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
from web3.utils.abi import (
    get_constructor_abi,
    merge_args_and_kwargs,
)
from web3.utils.contracts import (
    encode_abi,
)
from web3.utils.transactions import (
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
    abi, bytecode, bytecode_runtime = compile(filepath, contract_name)
    web3 = get_provider()
    deployment_data = create_deployement_data(web3, abi, bytecode)
    owner = Account.privateKeyToAccount(os.environ[owner_envvar])
    tx = create_transaction(web3, owner, deployment_data)
    signed_tx = Account.signTransaction(tx, owner.privateKey)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    click.echo('transaction hash: %s' % (encode_hex(tx_hash)))
    deploy_receipt = wait_for_transaction_receipt(web3, tx_hash)
    click.echo(deploy_receipt)


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


def get_provider():
    infura_token = os.environ['INFURA_ACCESS_TOKEN']
    provider = HTTPProvider('https://rinkeby.infura.io/%s' % (infura_token))
    return Web3(provider)


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
    tx = {
        'gas': 3000000,
        'gasPrice': 200000000,
        'nonce': web3.eth.getTransactionCount(owner.address),
        'data': deployment_data,
        'chainId': None,
        'to': '',
    }
    return tx


if __name__ == '__main__':
    run()
