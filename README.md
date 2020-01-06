# 0x2048-contracts

The 0x2048 project is a decentralized game of 2048 played over a state channel between a server and users. 0x2048-contracts is the Solidity contract code base for the the 0x2048 project. 

The contracts are found in `solidity/contracts`. This directory contains two contracts, `Arcade.sol`, and `SafeMath.sol`. `Arcade.sol` is the contract of interest while `SafeMath.sol` is borrowed from OpenZeppelin (https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/math/SafeMath.sol).

## 0x2048-Project

[Contracts](https://github.com/jstoxrocky/0x2048-contracts)

[Frontend](https://github.com/jstoxrocky/0x2048-frontend)

[Webserver](https://github.com/jstoxrocky/0x2048-webserver)

[Game](https://github.com/jstoxrocky/0x2048-game)

## Setup

```bash
$ pip install -r requirements.txt
```

Then follow instructions online to install solc. You can do this with homebrew.

## Test

Clone the repository. The Python wrapper around the solc compiler (py-solc) is deprecated. For this reason we run solc manually each time a change to the contract is made.

```bash
$ git submodule update --init --recursive
$ solc --combined-json abi,bin,bin-runtime -o bin --overwrite solidity/Arcade.sol
$ pytest
$ flake8
```

## Further Notes
"EIP-191 version 'E' is pretty broken, don't encourage its use": https://github.com
/ethereum/eth-account/commit/e4e2a8978fef90097f569e149c6a7010e3f45a98#diff-a9c6ca5d3c0ddc6c626bcee1142503c9

For this reasons the "Ethereum Signed Message" preamble is removed from Python and Solidity code.
