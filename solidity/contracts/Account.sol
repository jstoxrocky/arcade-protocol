pragma solidity ^0.4.16;


import './SafeMath.sol';


contract Account {
    using SafeMath for uint256;
    address public owner;
    mapping (address => uint256) public balances;

    function Account() public {
        owner = msg.sender;
    }

    function balanceOf(address _addr) view public returns (uint256) {
        return balances[_addr];
    }

    function lock() public payable {
        // Value gets sent to contract address
        balances[msg.sender] = msg.value;
    }

    function transferToOwner(
        bytes32 h, uint8 v, bytes32 r, bytes32 s, 
        address _addr, uint256 _value) public returns (address) {
        // Verify signer is user
        address signer = ecrecover(h, v, r, s);
        require(signer == _addr);
        // Verify that the function caller (owner) has supplied values contained in the signature
        bytes memory preamble = "\x19Ethereum Signed Message:\n32";
        bytes32 proof = keccak256(preamble, keccak256(this, _addr, _value));
        require(proof == h);
        // Decrement user's balance
        balances[_addr] -= _value;
        // Transfer value from contract to owner
        owner.transfer(_value);
    }
}
