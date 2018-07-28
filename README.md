# EVM Analyzer Benchmark Suite

## Introduction

This repo aims to be a collection of benchmarks suites for evaluating the precision of EVM code analysis tools

It started out as is a fork of Suhabe Bugara's excellent benchmark
suite, and [this
link](https://diligence.consensys.net/evm-analyzer-benchmark-suite)
shows the results of running some tools on tis benchmarks as of May
2018.

Another benchmark we add as a git submodule is Trail of Bits [(Not So) Smart Contracts](https://github.com/trailofbits/not-so-smart-contracts).

Some preliminary code has been written to run these on [Mythril](https://consensys.net/diligence/mythril.html).
With help, hopefully there will be code to run other tools over the benchmarks.

## Cloning

Since there is a git submodule in this repository clone using the `--recurse-submodules` option. For example:

```console
$ git clone https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite.git
```

## See also

Pull Pequests and suggestions and are welcome.

Please create a [new issue](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/issues/new) for ideas discussion.

The [wiki](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/wiki) has some commentary around the benchmarks.

See also [Building an Ethereum security benchmark](https://discourse.secureth.org/t/building-an-ethereum-security-benchmark/63).
