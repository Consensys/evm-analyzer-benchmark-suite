pragma solidity ^0.4.19;

interface Runner {
    function run(uint256 param) external;
}

contract ReentrancyNoStateEffect {

    function run(address base, uint256 param) public {
        Runner(base).run(param);
    }

}
