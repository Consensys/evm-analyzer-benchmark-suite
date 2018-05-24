//Adapted from Oyente paper
pragma solidity ^0.4.16;

contract Benchmark {
    address public owner ;
    bool public locked ;
    uint public reward ;
    bytes32 public diff ;
    bytes public solution;

    function Puzzle() public payable {
        owner = msg.sender;
        reward = msg.value;
        locked = false ;
        diff = bytes32 (11111); // pre - defined difficulty
    }

    function () public payable { // main code , runs at every invocation
        if ( msg.sender == owner ){ // update reward
            require (!locked);
            owner.transfer(reward);
            reward = msg.value;
        } else {
            if (msg.data.length > 0) { // submit a solution
                require (!locked);
                if ( sha256 (msg.data ) < diff ){
                    msg.sender.transfer(reward); // send reward
                    solution = msg.data;
                    locked = true;
                }
            }
        }
    }
}