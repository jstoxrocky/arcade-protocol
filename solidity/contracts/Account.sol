pragma solidity ^0.4.16;


import './SafeMath.sol';


/// @title Account
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
/// @dev Account logic for 0x2048 blockchain-integrated game
contract Account {
    using SafeMath for uint256;
    address public owner;
    uint256 public timeoutBlocks;
    mapping (address => uint256) public balances;
    mapping (address => uint256) public timeouts;

    function Account() public {
        owner = msg.sender;
        timeoutBlocks = 5;
    }

    /// @dev Function called by user to lock up ETH in contract
    /// @dev ETH must be locked to play games
    /// @dev Users send a signed message to the game server over state channel to allow withdrawls
    function balanceOf(address _addr) view public returns (uint256) {
        return balances[_addr];
    }

    function timeoutOf(address _addr) view public returns (uint256) {
        return timeouts[_addr];
    }

    function lock() public payable {
        // Value gets sent to contract address
        require(balances[msg.sender] == 0);
        balances[msg.sender] = msg.value;
        timeouts[msg.sender] = block.number + timeoutBlocks;
    }

    function transferToOwner(
        bytes32 h, uint8 v, bytes32 r, bytes32 s, 
        address _addr, uint256 _value) public {
        // Verify signer is user
        address signer = ecrecover(h, v, r, s);
        require(signer == _addr);
        // Verify that the function caller (owner) has supplied values contained in the signature
        bytes memory preamble = "\x19Ethereum Signed Message:\n32";
        bytes32 proof = keccak256(preamble, keccak256(this, _addr, _value));
        require(proof == h);
        // Decrement user's balance
        balances[_addr] = balances[_addr].sub(_value);
        // Transfer value from contract to owner
        owner.transfer(_value);
    }
}
