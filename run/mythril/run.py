#!/usr/bin/env python
"""
run  subhabe benchmarks with Mythril
"""
from pathlib import Path
from glob import glob
import json, subprocess, os, sys, time, yaml
import click

import pprint
pp = pprint.PrettyPrinter(indent=4)


def elapsed_str(elapsed):
    ""
    hours, rem = divmod(elapsed, 60 * 60)
    minutes, seconds = divmod(rem, 60)
    hours = int(hours)
    minutes = int(minutes)
    if hours:
        return ("{} hours, {} minute(s), {:5.2f} second(s)"
                .format(hours, minutes, seconds))
    elif minutes:
        return ("{} minute(s), {:5.2f} second(s)"
                .format(minutes, seconds))
    else:
        return ("{:5.2f} second(s)"
                .format(seconds))

def get_myth_prog():
    myth_prog = os.environ.get('MYTH', 'myth')
    cmd = [myth_prog, '--version']
    s = subprocess.run(cmd, stdout=subprocess.PIPE)
    if s.returncode != 0:
        print("Failed to get run Mythril with:\n\t{}\n failed with return code {}"
              .format(' '.join(cmd), s.returncode))
        return None
    # FIXME: check version
    return myth_prog

def run_myth(myth_prog, sol_file, debug):
    cmd = [myth_prog, '-x', '-o', 'json', '{}:Benchmark'.format(sol_file)]
    if debug:
        print(' '.join(cmd))
    start = time.time()
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    elapsed = (time.time() - start)
    return elapsed, result

def get_benchmark_yaml(mydir, suite_name, debug):
    testsuite_conf_path = mydir / (suite_name + '.yaml')
    if not testsuite_conf_path.exists():
        return {}
    testsuite_conf = yaml.load(open(testsuite_conf_path, 'r'))
    if debug:
        pp.pprint(testsuite_conf)
        print("-" * 30)
    return testsuite_conf

@click.command()
@click.option('--long-run', '-l', default=False,
              help="Run longer-running tests.")
@click.option('--verbose', '-v', default=False,
              help="Run longer-running tests.")
@click.option('--debug', '-d', default=False,
              help="Run longer-running tests.")
def run_benchmark_suite(long_run, verbose, debug):
    myth_prog = get_myth_prog()
    if not myth_prog:
        sys.exit(1)

    mydir = Path(__file__).parent.resolve()
    testsuite_conf = get_benchmark_yaml(mydir, 'suhabe', debug)
    testsuite_benchdir = mydir.parents[1] / 'benchmarks' / 'suhabe'
    os.chdir(testsuite_benchdir)

    # Zero counters
    unconfigured = invalid_execution = error_execution = 0
    ignored_benchmarks = unfound_issues = benchmarks = 0
    passed = 0
    total_time = 0.0

    # for sol_file in ['eth_tx_order_dependence_minimal.sol']:
    for sol_file in sorted(glob('*.sol')):
        benchmarks += 1
        print('-' * 40)
        print("Checking {}".format(sol_file))
        test_name = Path(sol_file).stem
        expected_data = testsuite_conf.get(test_name, None)
        if expected_data:
            if expected_data.get('ignore', None):
                print('Benchmark "{}" marked for ignoring; reason: {}'
                      .format(test_name, expected_data['reason']))
                ignored_benchmarks += 1
                continue
            elif expected_data.get('long', False) or long_run:
                print('Benchmark "{}" skipped because it takes a long time to run'
                      .format(test_name))
                ignored_benchmarks += 1
                continue

        cmd = [myth_prog, '-x', '-o', 'json', '{}:Benchmark'.format(sol_file)]
        if debug:
            print(' '.join(cmd))

        elapsed, s = run_myth(myth_prog, sol_file, debug)
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
            if debug:
                pp.pprint(data)
                print("=" * 30)
            if unconfigured > 2:
                break
        else:
            if data['error']:
                print('Benchmark "{}" errored'.format(test_name))
                error_execution += 1
                continue

            expected_issues = {(issue['address'], issue['title']): issue
                               for issue in expected_data['issues']}
            data_issues = data['issues']
            if len(expected_issues) != len(data_issues):
                print("Expecting to find {} issue(s), got {}"
                      .format(len(expected_issues), len(data_issues)))
                error_execution += 1
                benchmark_success = False
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
                        print("Mismatched issue datain {}".format(test_name))
                        pp.pprint(expected_issue)
                        print('.' * 40)
                        pp.pprint(issue)
                else:
                    print("Didn't find {} in {}"
                          .format(issue, test_name))
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

    print("\nSummary: {} benchmarks; {} passed {} unconfigured, {} invalid execution, "
          "{} errored, {} ignored."
          .format(benchmarks, passed, unconfigured, invalid_execution, error_execution,
                  ignored_benchmarks))
    print("Total elapsed execution time: {}".format(elapsed_str(total_time)))

if __name__ == '__main__':
    run_benchmark_suite()
