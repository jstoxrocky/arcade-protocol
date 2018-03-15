pragma solidity ^0.4.16;


import './SafeMath.sol';


/// @title Account
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
/// @dev Account logic for 0x2048 blockchain-integrated game
contract Account {
  using SafeMath for uint256;
  address public owner;
  uint256 public blockTimeout;
  mapping (address => uint256) public balances;
  mapping (address => uint256) public timeouts;
  mapping (address => uint256) public iousCount;
  uint256 public price;

  function Account() public {
    owner = msg.sender;
    blockTimeout = 60*60*24*7; // 1 week
    price = 1000000000000000; // 0.001 ETH
  }

  /// @dev Check the arcade account balance of a user.
  function balanceOf(address _addr) view public returns (uint256) {
    return balances[_addr];
  }

  /// @dev Check the arcade account timeout of a user.
  function timeoutOf(address _addr) view public returns (uint256) {
    return timeouts[_addr];
  }

  /// @dev Lock up ETH in state-channel with game server.
  /// @dev Signed IOU messages sent from user to server will allow users to play games
  /// @dev and the server to withdraw ETH from the user account. Funds can be withdrawn
  /// @dev by the user after the timeout. The contract owner cannot withdraw funds without
  /// @dev a signed message from the user for a specified amount.
  /// @dev Users are always in control of their funds.
  function deposit() public payable {
    // Require deposit to be a multiple of the price
    require(msg.value % price == 0);
    // Value gets sent to contract address
    balances[msg.sender] = balances[msg.sender].add(msg.value);
    // Add now to the timout if this is the first deposit for this user
    if (timeouts[msg.sender] == 0) {
      timeouts[msg.sender] = timeouts[msg.sender].add(now);
    }
    // Each time a deposit is made we increment the timeout by blockTimeout
    timeouts[msg.sender] = timeouts[msg.sender].add(blockTimeout);
  }

  /// @dev Unlock and withdraw ETH from state-channel.
  /// @dev Must be called after the timeout.
  function withdraw() view public {
    require(now > timeouts[msg.sender]);
    uint256 balance = balances[msg.sender];
    balances[msg.sender] = 0;
    msg.sender.transfer(balance);
  }

  function getNonce(address user) view public returns (uint256) {
    return iousCount[user];
  }

  /// @dev Transfer ETH from a user's arcade account to the game owner.
  /// @dev Transfers can only occur if the user signs and sends an IOU message
  /// @dev to the game server with the specified amount.
  /// @dev Users are always in control of their funds.
  function finalizeIOU(
    uint8 v, bytes32 r, bytes32 s,
    bytes32 schemaHash, address user, uint256 nonce) public {
    // Verify signer is user
    // We assume signature was signed with EIP712
    bytes32 messageHash = keccak256(schemaHash, keccak256(this, user, nonce));
    address signer = ecrecover(messageHash, v, r, s);
    require(signer == user);
    // Transferred value is hardcoded in the state channel.
    // A nonce is tracked in the contract.
    // Only a nonce one greater than the current value will be able to transfer
    // This is inefficient for state-channels as 1 payment requires 1 transaction
    // to the network, but it allows for a safer pay-per-play mechanism
    require(nonce == iousCount[user] + 1);
    // Decrement user's balance
    // Will throw if user does not have enough locked up
    // Onus is on the owner who recieved a signed state-channel IOU from the user
    // to withdraw before the timeout is up
    balances[user] = balances[user].sub(price);
    // Transfer value from contract to owner
    owner.transfer(price);
  }
}
