# Solidity Benchmark Suites for Evaluating EVM Code-Analysis tools, and Code to Run them

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Solidity Benchmark Suites for Evaluating EVM Code-Analysis tools, and Code to Run them](#solidity-benchmark-suites-for-evaluating-evm-code-analysis-tools-and-code-to-run-them)
    - [Introduction](#introduction)
    - [Cloning](#cloning)
    - [Creating reports for the existing Benchmarks](#creating-reports-for-the-existing-benchmarks)
    - [About Python Code to Run Benchmarks and Create Reports](#about-python-code-to-run-benchmarks-and-create-reports)
    - [See also](#see-also)

<!-- markdown-toc end -->


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
$ python runner/report.py --suite Suhabe
```

When done the directory `html/Suhabe/index.html` directory will contain the results.

## About Python Code to Run Benchmarks and Create Reports

We assme the benchmark suite repositories is set up using in git via the `--recurse-submodules` switch described above. With this in place, the two Python programs are run in sequence to:

* run an analyzer over a benchmark suite, and
* generate HTML reports for a benchmark suite that we have gathered data for in the previous step

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

The output of
[`runner/run.py`](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/runner/run.py)
is a YAML file which is stored in the folder
[`benchdata`](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/tree/master/benchdata)
with a subfolder under that with the name of the benchmark. For
example the output of `run.py` for the Suhabe benchmark suite will be a
file called `benchdata/Suhabe/Mythril.yaml`.

The second program, called
[`runner/report.py`](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/blob/master/runner/report.py),
takes the aforementioned data YAML file and creates a report from
that.  Currently it reads the data from a single analyzer. It needs to
be extended to read in data from all analyzers.

## See also

Pull Pequests and suggestions and are welcome.

Please create a [new issue](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/issues/new) for ideas discussion.

The [wiki](https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-benchmark-suite/wiki) has some commentary around the benchmarks.

See also [Building an Ethereum security benchmark](https://discourse.secureth.org/t/building-an-ethereum-security-benchmark/63).
