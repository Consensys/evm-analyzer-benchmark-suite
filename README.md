# Solidity Benchmark Suites for Evaluating EVM Code-Analysis tools, and Code to Run them

## Introduction

This repo aims to be a collection of benchmarks suites for evaluating the precision of EVM code analysis tools

It started out as is a fork of Suhabe Bugara's excellent benchmark
suite, and [this
link](https://diligence.consensys.net/evm-analyzer-benchmark-suite)
shows the results of runningrun some tools on this benchmarks as of May
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

There are two programs, `runner/run.py` gathers data and `runner/report.py` formats the data to HTML. 

### run.py
Executes specified benchmark suite.
Input arguments:
- `-s`, `--suite`       Benchmark suite name. Default `Suhabe`. Currently supported: `Suhabe`, `nssc`
- `-a`, `--analyser`    Analyser to benchmark. If not set all supported analysers will be benchmarked.
                        Currently supported: `Mythril`, `Manticore`
- `-v`, `--verbose`     More verbose output; use twice for the most verbose output
- `-t`, `--timeout`     Maximum time allowed on any single benchmark. Default 7 seconds
- `--files`             Print list of files in benchmark and exit

### report.py
Creates html report based on data generated after `run.py` execution (`benchdata/` directory)
Input arguments:
- `-s`, `--suite`       Benchmark suite name. Default `Suhabe`

### Example
Here is an example of complete report generation using Mythril on the Suhabe benchmark giving Mythril 5 minutes maximum to analyze a single benchmark:

```console
$ python runner/run.py --timeout 300 --suite Suhabe --analyser Mythril
$ python runner/report.py --suite Suhabe
```

When done the directory `html/Suhabe/index.html` directory will contain the results.

## Adding additional analyser to benchmark
Source code related to analysers is located in `runner/analysers/` module. In order to add support of a new analyser:
* Implement new class inherited from `BaseAnalyser`
* New class must be **imported** in `analyser/__init__.py`
* Create configuration files with expected output in `benchconf/`
Please check existing analysers as an example.

## See also

Pull Requests and suggestions and are welcome.

Please create a [new issue](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/issues/new) for ideas discussion.

The [wiki](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/wiki) has some commentary around the benchmarks.

See also [Building an Ethereum security benchmark](https://discourse.secureth.org/t/building-an-ethereum-security-benchmark/63).
