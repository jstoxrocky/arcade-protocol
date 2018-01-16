import pytest
from web3 import Web3
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from eth_utils import (
    to_checksum_address,
)
from ethereum import (
    tester,
)


@pytest.fixture(scope="module")
def web3():
    provider = EthereumTesterProvider()
    return Web3(provider)


@pytest.fixture(scope="module")
def owner_priv(web3):
    return tester.keys[1]


@pytest.fixture(scope="module")
def _owner_priv(web3):
    return tester.keys[3]


@pytest.fixture(scope="module")
def owner(web3):
    return to_checksum_address(tester.accounts[1])


@pytest.fixture(scope="module")
def user(web3):
    return to_checksum_address(tester.accounts[2])
