pragma solidity ^0.6.0;


import "./SafeMath.sol";


/// @title ArcadeProtocol
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
contract ArcadeProtocol {
    using SafeMath for uint256;
    using SafeMath for uint8;

    mapping (bytes32 => address payable) internal owners;
    mapping (bytes32 => uint256) internal prices;
    mapping (bytes32 => uint8) internal percentFees;
    mapping (bytes32 => uint256) internal highscores;
    mapping (bytes32 => uint256) internal jackpots;
    mapping (bytes32 => mapping (address => bytes32)) internal paymentCodes;

    function addGame(bytes32 gameId, uint256 price, uint8 percentFee) public {
        require(owners[gameId] == address(0), "Game ID already claimed");
        require(price > 0, "Game cannot be free to play");
        require(percentFee >= 0 && percentFee <= 100, "percentFee must be between 0 and 100");
        prices[gameId] = price;
        percentFees[gameId] = percentFee;
        owners[gameId] = msg.sender;
    }

    function getPrice(bytes32 gameId) public view returns (uint256) {
        return prices[gameId];
    }

    function getPaymentCode(bytes32 gameId, address addr) public view returns (bytes32) {
        return paymentCodes[gameId][addr];
    }

    function getHighscore(bytes32 gameId) public view returns (uint256) {
        return highscores[gameId];
    }

    function getJackpot(bytes32 gameId) public view returns (uint256) {
        return jackpots[gameId];
    }

    function getOwner(bytes32 gameId) public view returns (address) {
        return owners[gameId];
    }

    function getPercentFee(bytes32 gameId) public view returns (uint8) {
        return percentFees[gameId];
    }

    function pay(bytes32 gameId, bytes32 paymentCode) public payable {
        require(owners[gameId] != address(0), "Game must exist");
        require(msg.value == prices[gameId], "Value must be equal to price");
        paymentCodes[gameId][msg.sender] = paymentCode;
        jackpots[gameId] = jackpots[gameId].add(msg.value);
    }

    function claimHighscore(
        bytes32 gameId,
        uint256 score,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(owners[gameId] != address(0), "Game must exist");

        // EIP 191 Version 0
        address validator = address(this);
        bytes memory message = abi.encodePacked(
            byte(0x19), byte(0), validator, gameId, msg.sender, score
        );
        bytes32 messageHash = keccak256(message);
        address signer = ecrecover(messageHash, v, r, s);
        require(signer == owners[gameId], "Signer must be game owner");

        // Equality must be greater-than to prevent replay attacks
        require(score > highscores[gameId], "Score must be greater than highscore");

        // Winner!
        highscores[gameId] = score;
        uint256 fee = percentFees[gameId].mul(jackpots[gameId]).div(100);
        uint256 jackpot = jackpots[gameId] - fee;
        jackpots[gameId] = 0;
        owners[gameId].transfer(fee);
        msg.sender.transfer(jackpot);
    }
}
