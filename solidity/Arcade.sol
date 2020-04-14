pragma solidity ^0.6.0;


import "./SafeMath.sol";


/// @title Arcade
/// @author Joseph Stockermans (https://github.com/jstoxrocky)
contract Arcade {
    using SafeMath for uint256;
    mapping (bytes32 => address) internal owners;
    mapping (bytes32 => uint256) internal prices;
    mapping (bytes32 => uint256) internal highscores;
    mapping (bytes32 => uint256) internal jackpots;
    mapping (bytes32 => mapping (address => bytes32)) internal paymentCodes;

    function addGame(bytes32 gameId, uint256 price) public {
        require(owners[gameId] == address(0), "Game ID already claimed");
        require(price > 0, "Arcade cannot be free");
        prices[gameId] = price;
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

    function pay(bytes32 gameId, bytes32 paymentCode) public payable {
        require(owners[gameId] != address(0), "Game must exist");
        require(msg.value == prices[gameId], "Value is not equal to price");
        paymentCodes[gameId][msg.sender] = paymentCode;
        jackpots[gameId] = jackpots[gameId].add(msg.value);
    }

    function claim(
        bytes32 gameId,
        uint256 score,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(owners[gameId] != address(0), "Game must exist");

        // The user uploads their score along with the signature
        // from the Arcade server. Since the user's address forms part
        // of the signature, it is necessary that the user who paid the
        // Arcade server be the one to transact to this method.

        // Although the signing account is owned by the Arcade, it is
        // necessary to follow the preventative measure against replay-attacks
        // outlined in EIPs 191 and 712. Preventing Ethereum transactions from
        // being signed (Geth PR 2940, EIP 191, EIP 712) is not necessarily a
        // concern here since the signing account controlled by the Arcade.
        // Likewise, EIP 712's strict guidelines for encoding an arbitrary
        // structured message to bytes is not necessarily a concern either
        // since the Arcade again controls the signing logic. However, since
        // the only downside to added these security measures is an increase
        // in gas to power the method, and the method is executed by the user,
        // it is easier to not "roll our own crypto" here and just use EIP 712's
        // guidelines for signing.

        // After the signer is verified to be the Arcade server the
        // score is checked to ensure that it is not greater than the
        // current highscore. If these checks pass, the highscore is
        // updated and the value of the jackpot is transferred to the message
        // sender.

        // EIP 191 Version 1 (EIP 712)

        // Precompute
        // bytes32 domainTypeHash = keccak256('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)');
        // bytes32 name = keccak256('0x2048')
        // bytes32 version = keccak256('1.0')
        // chainId = 1;
        // bytes32 highscoreTypeHash = keccak256('Highscore(address user,uint256 score,bytes32 gameId)');

        bytes32 domainSeparator = keccak256(
            abi.encode(
                0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f, // domainTypeHash
                0xa7fc84919e7612cb73ee05a72c871940b9845869baf1a644b713770b676b2525, // name
                0xe6bbd6277e1bf288eed5e8d1780f9a50b239e86b153736bceebccf4ea79d90b3, // version
                1, // chainId
                address(this) // validator
            )
        );
        bytes32 hashStruct = keccak256(
            abi.encode(
                0x5fd1283d41895a588826aa1d924843728619a715ea50136c5c11f53e4d52e9c2, // highscoreTypeHash
                msg.sender,
                score,
                gameId
            )
        );
        bytes32 messageHash = keccak256(
            abi.encodePacked(
                byte(0x19), // preamble
                byte(0x01), // version
                domainSeparator,
                hashStruct
            )
        );
        address signer = ecrecover(messageHash, v, r, s);
        require(signer == owners[gameId], "Signer is not game owner");

        // User must have scored higher than highscore.
        // This must be greater-than to prevent replay attacks.
        require(score > highscores[gameId], "Score is not greater than highscore");
        // Send jackpot to address included in hashed-signed message
        // Reset jackpot
        highscores[gameId] = score;
        uint256 currentJackpot = jackpots[gameId];
        jackpots[gameId] = 0;
        msg.sender.transfer(currentJackpot);
    }
}
