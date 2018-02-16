pragma solidity ^0.4.16;


import './SafeMath.sol';


contract Account {
    using SafeMath for uint256;
    address public owner;
    mapping (address => uint256) public balances;
    mapping (address => uint256) public timeouts;

    function Account() public {
        owner = msg.sender;
    }

    function balanceOf(address _addr) view public returns (uint256) {
        return balances[_addr];
    }

    function timeoutOf(address _addr) view public returns (uint256) {
        return timeouts[_addr];
    }

    function lock(uint256 _timeout) public payable {
        balances[msg.sender] += msg.value;
        timeouts[msg.sender] = _timeout;
    }
}
