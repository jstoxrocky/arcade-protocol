pragma solidity ^0.4.16;


import './SafeMath.sol';


/// @title Arcade
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
/// @dev Payment logic for 0x2048 blockchain-integrated game
contract Arcade {


	using SafeMath for uint256;
	mapping (uint256 => mapping (address => bool)) public participants;
	uint256 public round;
	uint256 private highscore;
	uint256 public jackpot;
	uint256 public price;
	address public owner;
	uint256 public percentFee;


	function Arcade() public {
		// Set initial values
		// Initial price is set to 0.01 ETH (~$0.25)
		// Fees are set to 10% (~$0.03 cent on $0.25 payments)
		highscore = 0;
		jackpot = 0;
		round = 1;
		price = 250000000000000; 
		owner = msg.sender;
		percentFee = 10;
	}


	/// @dev Function called by user to pay service and be able to play in this round
	/// @dev User must pay an amount equal to the variable price
	/// @dev User is prevented from paying more than once as you only need to pay once to play in a round 
	function pay() public payable {
		// User has paid correct amount
		uint256 _value = msg.value;
		require(_value == price);

		// User has not already paid before
		bool isAlreadyParticipant = getParticipation(msg.sender);
		require(!isAlreadyParticipant);

		// Log this value to our participants data blob
		participants[round][msg.sender] = true;

		// Calculate fees and this payment's contribution to the jackpot
		uint256 fee = (_value.div(100)).mul(percentFee);
		uint256 toJackpot = _value.sub(fee);

		// Increment jackpot and transfer fees
		jackpot = jackpot.add(toJackpot);
		owner.transfer(fee);
	}


	/// @dev Lookup whether a given user has already paid for this round
    /// @param _addr Lookup participation for this address
    /// @return boolean representing whether the user has paid for this round already
	function getParticipation(address _addr) view public returns (bool) {
		return participants[round][_addr];
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

		// User is a participant 
		// Need to be a participant to check to see if score > highscore
		bool isParticipant = getParticipation(_addr);
		require(isParticipant);

		// User must have gotten higher than highscore
		require(score > highscore);

		// Send jackpot to address included in hashed-signed message 
		// Reset jackpot and deposits
		round = round.add(1);
		highscore = score;
		_addr.transfer(jackpot);
		jackpot = 0;
	}


	/// @dev Function for a user to adjust the price per round 
	/// @dev Prices will only be uploaded if they have been signed by 0x2048
    /// @param h The hashed message that was signed
    /// @param v The `v` parameter from the signature
    /// @param r The `r` parameter from signature
    /// @param s The `s` parameter from signature
    /// @param _price The new price
	function adjustPrice(bytes32 h, uint8 v, bytes32 r, bytes32 s, address _addr, uint256 _price) public {
		// Verify signer is 0x2048
		address signer = ecrecover(h, v, r, s);
		require(signer == owner);

		// Verify that the user has supplied values contained in the signature
		bytes memory preamble = "\x19Ethereum Signed Message:\n32";
		bytes32 proof = keccak256(preamble, keccak256(this, _addr, _price));
		require(proof == h);

		// Adjust price
		price = _price;
	}

}