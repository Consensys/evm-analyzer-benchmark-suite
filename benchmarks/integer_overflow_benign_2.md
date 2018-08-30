This example was derived from [an actual safe math library](
https://github.com/Modular-Network/ethereum-libraries/blob/master/BasicMathLib/BasicMathLib.sol)

```solidity
//Single transaction overflow
//Post-transaction effect: overflow nevers escapes to publicly-readable storage
```

Ideally tools wouldn't report an overflow bug on this benchmark, even
though the variable, `res` itself actually overflows.
