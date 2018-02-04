# 0x2048-contracts

The 0x2048 project is a decentralized game of 2048 played over a state channel between a server and users. 0x2048-contracts is the Solidity contract code base for the the 0x2048 project. 

The contracts are found in `solidity/contracts`. This directory contains two contracts, `Arcade.sol`, and `SafeMath.sol`. `Arcade.sol` is the contract of interest while `SafeMath.sol` is borrowed from OpenZeppelin (https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/math/SafeMath.sol).

## Setup

```bash
$ pip install -r requirements.txt
$ python -m solc.install v0.4.19
$ export SOLC_BINARY=$HOME/.py-solc/solc-v0.4.19/bin/solc
$ export LD_LIBRARY_PATH=$HOME/.py-solc/solc-v0.4.19/bin
```

## Test

Clone the repository

```bash
$ pytest
```
