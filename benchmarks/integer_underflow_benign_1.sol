//Single transaction underflow
//Post-transaction effect: underflow never escapes function

pragma solidity ^0.4.19;

contract IntegerUnderflowBenign1 {
    uint public count = 1;

    function run(uint256 input) public {
        uint res = count - input;
    }
}
