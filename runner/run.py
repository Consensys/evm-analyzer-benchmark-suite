#!/usr/bin/env python
"""
top-level CLI to run benchmarks
"""
from pathlib import Path
from glob import glob
import json, os, sys, yaml
import click

import pprint
pp = pprint.PrettyPrinter(indent=4)

project_root_dir = Path(__file__).parent.resolve()

# Make relative loading work without relative import, which
# doesn't work with main programs
sys.path.insert(0, project_root_dir)
from mythstuff import get_myth_prog, run_myth


# Maximum time, in seconds, that we allow the analyzer to
# take in analyzing a benchmark.
DEFAULT_TIMEOUT=7.0


def elapsed_str(elapsed):
    "Format `elapsed` into a human-readable string with hours, minutes and seconds"
    hours, rem = divmod(elapsed, 60 * 60)
    minutes, seconds = divmod(rem, 60)
    secs_plural = 's' if seconds != 1.0 else ''
    hours = int(hours)
    minutes = int(minutes)
    mins_plural = 's' if minutes != 1.0 else ''
    if hours:
        return ("{} hours, {} minute{}, {:5.2f} second{}"
                .format(hours, minutes, mins_plural,
                        seconds, secs_plural))
    elif minutes:
        return ("{} minute{}, {:5.2f} second{}"
                .format(minutes, mins_plural,
                        seconds, secs_plural))
    else:
        return ("{:5.2f} second{}"
                .format(seconds, secs_plural))

def get_benchmark_yaml(mydir, suite_name, debug):
    testsuite_conf_path = mydir / (suite_name + '.yaml')
    if not testsuite_conf_path.exists():
        return {}
    testsuite_conf = yaml.load(open(testsuite_conf_path, 'r'))
    if debug:
        pp.pprint(testsuite_conf)
        print("-" * 30)
    return testsuite_conf

def gather_benchmark_files(root_dir, suite_name):
    testsuite_benchdir = root_dir.parent / 'benchmarks' / suite_name
    os.chdir(testsuite_benchdir)
    return sorted(glob('**/*.sol', recursive=True))


# TODO add json config lint function?
@click.command()
@click.option('--suite', '-s', type=click.Choice(['suhabe', 'nssc',
                                                  'not-so-smart-contracts']),
              default='suhabe',
              help="Benchmark suite to run; "
              "nscc is an abbreviation for not-so-smart-contracts.")
@click.option('--verbose', '-v', count=True,
              help="More verbose output; use twice for the most verbose output.")
@click.option('--timeout', '-t', type=float,
              default=DEFAULT_TIMEOUT,
              help="Maximum time allowed on any single benchmark.")
@click.option('--files/--no-files', default=False,
              help="List files in benchmark and exit.")
def run_benchmark_suite(suite, verbose, timeout, files):
    """Run Mythril on a benchmark suite.

    If you set environment variable MYTH, that will be used a the myth CLI command to
    invoke. If that is not set, we run using "myth".
    """
    myth_prog = get_myth_prog()
    if not myth_prog:
        sys.exit(1)

    if suite == 'nssc':
        suite = 'not-so-smart-contracts'

    debug = verbose == 2
    testsuite_conf = get_benchmark_yaml(project_root_dir, suite, debug)
    benchmark_files = gather_benchmark_files(project_root_dir, suite)

    # Zero counters
    unconfigured = invalid_execution = error_execution = 0
    ignored_benchmarks = unfound_issues = benchmarks = 0
    timed_out = passed = 0
    total_time = 0.0

    if files:
        print("Benchmark suite {} contains {} files:".format(suite, len(benchmark_files)))
        for bench_name in benchmark_files:
            print("\t", bench_name)
        sys.exit(0)

    print("Running {} benchmark suite".format(suite))

    # for sol_file in ['eth_tx_order_dependence_minimal.sol']:
    for sol_file in benchmark_files:
        benchmarks += 1
        print('-' * 40)
        print("Checking {}".format(sol_file))
        sol_path = Path(sol_file)
        test_name = str(sol_path.parent / sol_path.stem)
        expected_data = testsuite_conf.get(test_name, None)

        if expected_data:
            run_time = expected_data.get('run_time', timeout)
            if expected_data.get('ignore', None):
                print('Benchmark "{}" marked for ignoring; reason: {}'
                      .format(test_name, expected_data['reason']))
                ignored_benchmarks += 1
                continue
            elif timeout < run_time:
                print('Benchmark "{}" skipped because it is noted to take a long time; '
                      '{} seconds'
                      .format(test_name, run_time))
                ignored_benchmarks += 1
                continue

        cmd = [myth_prog, '-x', '-o', 'json', '{}'.format(sol_file)]
        if verbose:
            print(' '.join(cmd))

        elapsed, s = run_myth(myth_prog, sol_file, debug, timeout)
        if s is None:
            print('Benchmark "{}" timed out after {}'.format(test_name, elapsed_str(elapsed)))
            timed_out += 1
            continue

        total_time += elapsed
        print(elapsed_str(elapsed))

        if s.returncode != 0:
            print("mythril invocation:\n\t{}\n failed with return code {}"
                  .format(' '.join(cmd), s.returncode))
            invalid_execution += 1
            continue
        data = json.loads(s.stdout)
        if debug:
            pp.pprint(data)
            print("=" * 30)

        benchmark_success = True
        if not expected_data:
            unconfigured += 1
            print('Benchmark "{}" results not configured, '
                  'so I cannot pass judgement on this'.format(test_name))
            pp.pprint(data)
            print("=" * 30)
            if unconfigured > 5:
                break
        else:
            if data['error']:
                print('Benchmark "{}" errored'.format(test_name))
                print(data['error'])
                error_execution += 1
                continue

            expected_issues = {(issue['address'], issue['title']): issue
                               for issue in expected_data['issues']}
            data_issues = data['issues']
            if len(expected_issues) != len(data_issues):
                print("Expecting to find {} issue(s), got {}"
                      .format(len(expected_issues), len(data_issues)))
                error_execution += 1
                pp.pprint(data_issues)
                print("=" * 30)
                continue

            if verbose and not data_issues:
                print("No problems found and none expected")
                continue

            for issue in data_issues:
                expected_issue = expected_issues.get((issue['address'], issue['title']),
                                                     None)
                if expected_issue:
                    # When the code is too long, we skip it in the YAML
                    if (expected_issue.get('code', issue['code']) != issue['code']
                        or expected_issue['title'] != issue['title']):
                        print("Mismatched issue data in {}".format(test_name))
                        pp.pprint(expected_issue)
                        print('.' * 40)
                        pp.pprint(issue)
                        benchmark_success = False
                else:
                    print("Didn't find {} in {}"
                          .format(issue, test_name))
                    pp.pprint(data_issues)
                    unfound_issues += 1
                    benchmark_success = False
            if benchmark_success:
                passed += 1
                print('Benchmark "{}" checks out'.format(test_name))
                if verbose:
                    for num, issue in enumerate(data_issues):
                        print("  Issue {1}. {0[type]} {0[title]} "
                              "at address {0[address]}:\n\t{0[code]}"
                              .format(issue, num))
                        pass
                    pass
                pass
            pass

        # print(data)
        pass
    print('-' * 40)

    print("\nSummary: {} benchmarks; {} passed, {} unconfigured, {} aborted abnormally, "
          "{} unexpected results, {} timed out, {} ignored."
          .format(benchmarks, passed, unconfigured, invalid_execution, error_execution,
                  timed_out, ignored_benchmarks))
    print("Total elapsed execution time: {}".format(elapsed_str(total_time)))

if __name__ == '__main__':
    run_benchmark_suite()
