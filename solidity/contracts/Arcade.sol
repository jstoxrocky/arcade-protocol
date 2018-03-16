pragma solidity ^0.4.18;


import "./dependencies/SafeMath.sol";


/// @title Arcade
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
/// @dev Payment logic for 0x2048 blockchain-integrated game
contract Arcade {
    using SafeMath for uint256;
    uint256 public round;
    uint256 public highscore;
    uint256 public jackpot;
    address public owner;
    uint256 public percentFee;

    function Arcade() public {
        // Set initial values
        // Initial price is set to 0.01 ETH (~$0.25)
        // Fees are set to 10% (~$0.03 cent on $0.25 payments)
        highscore = 0;
        jackpot = 0;
        round = 1;
        owner = msg.sender;
        percentFee = 10;
    }

    /// @dev Function for a user to upload their highscore
    /// @dev Scores will only be uploaded if they have been signed by 0x2048
    /// @dev We don't care about msg.sender, instead we focus on the address signed by 0x2048
    /// @param h The hashed message that was signed
    /// @param v The `v` parameter from the signature
    /// @param r The `r` parameter from signature
    /// @param s The `s` parameter from signature
    /// @param score The user's score
    /// @param _addr The user's address
    function uploadScore(bytes32 h, uint8 v, bytes32 r, bytes32 s, address _addr, uint256 score) public {
        // Verify signer is 0x2048
        address signer = ecrecover(h, v, r, s);
        require(signer == owner);

        // Verify that the user has supplied values contained in the signature
        bytes memory preamble = "\x19Ethereum Signed Message:\n32";
        bytes32 proof = keccak256(preamble, keccak256(this, _addr, score));
        require(proof == h);

        // User must have gotten higher than highscore
        require(score > highscore);

        // Send jackpot to address included in hashed-signed message
        // Reset jackpot and deposits
        round = round.add(1);
        highscore = score;
        jackpot = 0;
        _addr.transfer(jackpot);
    }
}