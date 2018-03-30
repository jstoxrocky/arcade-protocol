pragma solidity ^0.4.18;


import "./SafeMath.sol";


/// @title Arcade
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
/// @dev Payment logic for 0x2048 blockchain-integrated game
contract Arcade {
    using SafeMath for uint256;
    address public owner;
    uint256 public jackpot;
    uint256 public highscore;
    uint256 public price;
    uint256 public round;
    mapping (address => bytes32) public nonces;

    function Arcade() public {
        // Set initial values
        // Initial price is set to 0.01 ETH (~$0.25)
        // Fees are set to 10% (~$0.03 cent on $0.25 payments)
        highscore = 0;
        jackpot = 0;
        round = 1;
        price = 1000000000000000; // 0.001 ETH
        owner = msg.sender;
    }

    /// @dev Function called by user to pay service and be able to play in this round
    /// @dev User must pay an amount equal to the variable price
    function pay(bytes32 nonce) public payable {
        require(msg.value == price);
        nonces[msg.sender] = nonce;
        jackpot = jackpot.add(msg.value);
    }

    function getNonce(address addr) public view returns (bytes32) {
        return nonces[addr];
    }

    /// @dev Function for a user to upload their highscore
    /// @dev Scores will only be uploaded if they have been signed by 0x2048
    /// @dev We don't care about msg.sender, instead we focus on the address signed by 0x2048
    /// @param v The `v` parameter from the signature
    /// @param r The `r` parameter from signature
    /// @param s The `s` parameter from signature
    /// @param score The user's score
    /// @param user The user's address
    function uploadScore(
        uint8 v, 
        bytes32 r, 
        bytes32 s, 
        address user, 
        uint256 score
    ) public {
        // Verify signer
        bytes memory preamble = "\x19Ethereum Signed Message:\n32";
        bytes32 messageHash = keccak256(preamble, keccak256(this, user, score));
        address signer = ecrecover(messageHash, v, r, s);
        require(signer == owner);
        // User must have gotten higher than highscore
        require(score > highscore);
        // Send jackpot to address included in hashed-signed message
        // Reset jackpot
        highscore = score;
        round = round.add(1);
        uint256 currentJackpot = jackpot;
        jackpot = 0;
        user.transfer(currentJackpot);
    }
}