# Solidity Benchmark Suites for Evaluating EVM Code-Analysis tools, and Code to Run them

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Solidity Benchmark Suites for Evaluating EVM Code-Analysis tools, and Code to Run them](#solidity-benchmark-suites-for-evaluating-evm-code-analysis-tools-and-code-to-run-them)
    - [Introduction](#introduction)
    - [Cloning](#cloning)
    - [Benchmarks have changed?](#benchmarks-have-changed)
    - [Project setup](#project-setup)
    - [About Python Code to Run Benchmarks and Create Reports](#about-python-code-to-run-benchmarks-and-create-reports)
    - [Adding additional analyser to benchmark](#adding-additional-analyser-to-benchmark)
    - [See also](#see-also)

<!-- markdown-toc end -->


## Introduction

This repo aims to be a collection of benchmarks suites for evaluating the precision of EVM code analysis tools.

If you just want to see the reports created as a result of running the various analyzers over the benchmark suites, you can find that [here](https://ethereumanalysisbenchmarks.github.io/). 

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

### Forgot to `--recurse-submodules` on clone

_Only_ If you forget the `--recurse-submodules` on the `git clone` do the following:

```console
$ git submodule init
Submodule 'benchmarks/Suhabe' (https://github.com/ConsenSys/evm-analyzer-benchmark-suite.git) registered for path 'benchmarks/Suhabe'
Submodule 'benchmarks/nssc' (https://github.com/trailofbits/not-so-smart-contracts.git) registered for path 'benchmarks/nssc'
$ git submodule update
Cloning into '/src/external-vcs/github/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/benchmarks/Suhabe'...
Cloning into '/src/external-vcs/github/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/nchmarks/nssc'...
...
```

## Benchmarks have changed?

If benchmarks change and you want to pull in the new benchmark code, use `git submodule update`.

## Project setup

The reports programs are written in Python 3.6 or better. To install dependent Python packages, run:
```console
$ pip install -r requirements.txt
```

## About Python Code to Run Benchmarks and Create Reports

We assme the benchmark suite repositories is set up using in git via the `--recurse-submodules` switch described above. With this in place, the two Python programs are run in sequence to:

* run an analyzer over a benchmark suite, and
* generate HTML reports for a benchmark suite that we have gathered data for in the previous step

### runner/run.py (https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/runner/run.py)
Executes specified benchmark suite.
Input arguments:
- `-s`, `--suite`       Benchmark suite name. Default `Suhabe`. Currently supported: `Suhabe`, `nssc`
- `-a`, `--analyser`    Analyser to benchmark. If not set all supported analysers will be benchmarked.
                        Currently supported: `Mythril`, `Manticore`
- `-v`, `--verbose`     More verbose output; use twice for the most verbose output
- `-t`, `--timeout`     Maximum time allowed on any single benchmark. Default 7 seconds
- `--files`             Print list of files in benchmark and exit  

**Description:**
The first program `runner/run.py` takes a number of command-line
arguments; one of them is the name of a benchmark suite. From that it
reads two YAML configuration files for the benchmark. The first YAML
file has information about the benchmark suite: the names of the files
in the benchmarks, whether the benchmark is supposed to succeed or
fail with a vulnerability, and possibly other information. An example
of such a YAML file is
[benchconf/Suhabe.yaml](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/benchconf/Suhabe.yaml). The
other YAML input configuration file is specific to the analyzer. For
Mythril on the Suhabe benchmark, it is called
[benchconf/Suhabe-Mythril.yaml](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/benchconf/Suhabe-Mythril.yaml)

For each new Benchmark suite, these two YAML files will need to
exist. The second one you can start out with an empty file.

The output is a YAML file which is stored in the folder
[`benchdata`](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/tree/master/benchdata)
with a subfolder under that with the name of the benchmark. For
example the output of `run.py` for the Suhabe benchmark suite will be a
file called `benchdata/Suhabe/Mythril.yaml`.

### runner/report.py (https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/runner/report.py)
Takes the aforementioned data YAML files and creates a HTML report from that.  
Input arguments:
- `-s`, `--suite`       Benchmark suite name. Default `Suhabe`,


Here is an example of complete report generation using Mythril on the Suhabe benchmark giving Mythril 5 minutes maximum to analyze a single benchmark:

```console
$ python runner/run.py --timeout 300 --suite Suhabe --analyser Mythril
$ python runner/report.py --suite Suhabe
```

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
