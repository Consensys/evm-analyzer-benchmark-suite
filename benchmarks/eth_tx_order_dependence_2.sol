pragma solidity ^0.4.16;

contract EthTxOrderDependence2 {
    uint256 public reward;
    address owner;

    function EthTxOrderDependence2() {
        owner = msg.sender;
    }

    function setReward() public payable {
        require(msg.sender == owner);

        owner.transfer(reward); //refund previous reward
        reward = msg.value;
    }
}
