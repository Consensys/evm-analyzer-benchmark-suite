This example was derived from [an actual safe math library](
https://github.com/Modular-Network/ethereum-libraries/blob/master/BasicMathLib/BasicMathLib.sol)

```solidity
//Single transaction overflow
//Post-transaction effect: overflow never escapes function
```

Note that

```solidity
    function run(uint256 input) public {
        uint res = count - input;
    }
```

is equivalent to

```solidity
    function run(uint256 input) public {
        ;
    }
```


Ideally tools wouldn't report an overflow bug on this benchmark, even
though the variable, `res` itself actually overflows.
