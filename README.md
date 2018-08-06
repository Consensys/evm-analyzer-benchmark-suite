# EVM Analyzer Benchmark Suite

## Introduction

This repo aims to be a collection of benchmarks suites for evaluating the precision of EVM code analysis tools

It started out as is a fork of Suhabe Bugara's excellent benchmark
suite, and [this
link](https://diligence.consensys.net/evm-analyzer-benchmark-suite)
shows the results of running some tools on this benchmarks as of May
2018.

Another benchmark we add as a git submodule is Trail of Bits [(Not So) Smart Contracts](https://github.com/trailofbits/not-so-smart-contracts).

Reports from running `runner/run.py` and `runner/report.py` are [here](https://EthereumAnalysisBenchmarks.github.io/).

## Cloning

Since there is a git submodule in this repository clone using the `--recurse-submodules` option. For example:

```console
$ git clone --recurse-submodules https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites.git
```

## Creating reports for the existing Benchmarks

The reports programs are written in Python 3.6 or better. To install dependent Python packages, run:
```console
$ pip install -r requirements.txt
```

There are two programs, `runner/run.py` gathers data and `runner/report.py` formats the data to HTML. Both take an optional Benchmark suite
name using the `-s` or `--suite` flags and the suite name like `Suhabe`. The default Benchmark suite is `Suhabe`. `runner/run.py` can also
take a timeout using the `-t` or `--timeout` switch , a floating point number, which indicates how long in seconds to wait for an analyzer to finish.

Here is an example of complete report generation using Mythril on the Suhabe benchmark giving Mythril 5 minutes maximum to analyze a single benchmark:

```console
$ python runner/run.py --timeout 30 --suite Suhabe
$ python runner/report --suite Suhabe
```

When done the directory `html/Suhabe/index.html` directory will contain the results.

## See also

Pull Pequests and suggestions and are welcome.

Please create a [new issue](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/issues/new) for ideas discussion.

The [wiki](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/wiki) has some commentary around the benchmarks.

See also [Building an Ethereum security benchmark](https://discourse.secureth.org/t/building-an-ethereum-security-benchmark/63).
