**This code comes with absolutely no warranty or guarantees of correctness.**

This repository is in no way associated with JLC, LCS or any other company or entity associated with them.

The person who wrote this is not a talented developer or capable individual.

## Installation
You should be able yo just run `pip install .` and be on your way.
This should not require any non standard libraries


## Tools

### jlcsearch

`jlcsearch --help` for usage

Exposes a slightly less horrid interface to the JLC catalog.
By default only returns the first and cheapest basic/preferred part.
Any occurrences of `OHM` in the keyword will be replaced with the Ω symbol.



### jlcbomcheck

`jlcbomcheck --help` for usage

Tries to verify that the LCSC part codes in a kicad BOM file are correct.
This is done by checking that the case is roughly correct and that the description is neat enough.
Will also check component values when it thinks that it can.
**THIS IS OBVIOUSLY NOT EXHAUSTIVE**
