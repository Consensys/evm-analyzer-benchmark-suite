pragma solidity ^0.4.19;

contract AssertSym {
    function run(uint256 param) public {
        assert(param > 0);
    }
}
