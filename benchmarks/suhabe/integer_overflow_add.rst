Integer Overflow (state modifying)
==================================

.. literalinclude:: integer_overflow_add.sol

This is an example of an integer overflow bug that allows an attacker to directly set an overflow condition
and let them set the value of ``count`` to whatever they want.
In the original specification, the developer of this application might have intended that ``count`` would allow
be allowed to be incremented from it's previous number (for example, in minting new tokens).

However, due to this vulnerability the attacker is able to set ``count`` to 0 by sending ``MAX_UINT256 - 1``
(which is ``2**256 - 2``) for the argument ``input``, which is at the very least unintended behavior.

More extreme versions of this bug were the basis for the following public mainnet explots: [DB_ENTRY], etc.
