#!/usr/bin/env python
"""
top-level CLI to run benchmarks
"""
from pathlib import Path
from glob import glob
import json, os, sys, time, yaml
import click

import pprint
pp = pprint.PrettyPrinter(indent=4)

code_root_dir = Path(__file__).parent.resolve()
project_root_dir = code_root_dir.parent

# Make relative loading work without relative import, which
# doesn't work with main programs
sys.path.insert(0, code_root_dir)
from mythstuff import get_myth_prog, run_myth


# Maximum time, in seconds, that we allow the analyzer to
# take in analyzing a benchmark.
DEFAULT_TIMEOUT=7.0


def secs_to_human(elapsed):
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

def get_benchmark_yaml(project_root_dir, suite_name, analyzer, debug):
    testsuite_conf_path = project_root_dir / 'benchconf' / "{}.yaml".format(suite_name)
    if not testsuite_conf_path.exists():
        return {}
    testsuite_conf = yaml.load(open(testsuite_conf_path, 'r'))
    analyzer_conf_path = project_root_dir / 'benchconf' / "{}-{}.yaml".format(suite_name, analyzer)
    analyzer_conf  = yaml.load(open(analyzer_conf_path, 'r'))
    # Merge two configurations
    conf = {**testsuite_conf, **analyzer_conf}
    # We still need to values are themselves dictionaries
    for k, v in conf.items():
        if isinstance(v, dict):
            conf[k] = {**v, **testsuite_conf[k]}
            pass
        pass
    if debug:
        pp.pprint(conf)
        print("-" * 30)
    return conf

def gather_benchmark_files(root_dir, suite_name, benchmark_subdir):
    testsuite_benchdir = root_dir.parent / 'benchmarks' / suite_name / benchmark_subdir
    os.chdir(testsuite_benchdir)
    return sorted(glob('**/*.sol', recursive=True))

# TODO add json config lint function?
@click.command()
@click.option('--suite', '-s', type=click.Choice(['Suhabe', 'nssc',
                                                  'not-so-smart-contracts']),
              default='Suhabe',
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
    analyzer = 'Mythril'

    if analyzer == 'Mythril':
        analyzer_prog, myth_version = get_myth_prog()
        if not analyzer_prog:
            sys.exit(1)
            pass
        print("Using {} {}".format(analyzer, myth_version))
        pass

    out_data = {'analyzer': analyzer}
    out_data = {'mythril_version': myth_version}
    if suite == 'nssc':
        suite = 'not-so-smart-contracts'

    out_data['suite'] = suite
    out_data['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    debug = verbose == 2
    testsuite_conf = get_benchmark_yaml(project_root_dir, suite, analyzer, debug)
    benchmark_files = gather_benchmark_files(code_root_dir, suite,
                                             testsuite_conf['benchmark_subdir'])

    # Zero counters
    unconfigured = invalid_execution = error_execution = 0
    ignored_benchmarks = unfound_issues = benchmarks = 0
    timed_out = expected = 0
    total_time = 0.0

    out_data['benchmark_files'] = benchmark_files
    if files:
        print("Benchmark suite {} contains {} files:".format(suite, len(benchmark_files)))
        for bench_name in benchmark_files:
            print("\t", bench_name)
        sys.exit(0)

    print("Running {} benchmark suite".format(suite))

    out_data['benchmarks'] = {}
    # for sol_file in ['eth_tx_order_dependence_minimal.sol']:
    for sol_file in benchmark_files:
        benchmarks += 1
        print('-' * 40)
        print("Checking {}".format(sol_file))
        sol_path = Path(sol_file)
        test_name = str(sol_path.parent / sol_path.stem)
        bench_data = out_data['benchmarks'][test_name] = {}
        expected_data = testsuite_conf.get(test_name, None)
        bench_data['bug_type'] = expected_data.get('bug_type', 'Unknown')
        bench_data['expected_data'] = expected_data
        if expected_data:
            run_time = expected_data.get('run_time', timeout)
            if expected_data.get('ignore', None):
                print('Benchmark "{}" marked for ignoring; reason: {}'
                      .format(test_name, expected_data['reason']))
                ignored_benchmarks += 1
                bench_data['result'] = 'Ignored'
                bench_data['elapsed_str'] = 'ignored'

                continue
            elif timeout < run_time:
                # When the code is too long, we skip it in the YAML
                print('Benchmark "{}" skipped because it is noted to take a long time; '
                      '{} seconds'
                      .format(test_name, run_time))
                ignored_benchmarks += 1
                bench_data['result'] = 'Too Long'
                bench_data['elapsed_str'] = secs_to_human(run_time)
                continue

        # FIXME: expand to other analyzers
        cmd = [analyzer_prog, '-x', '-o', 'json', '{}'.format(sol_file)]
        if verbose:
            print(' '.join(cmd))

        elapsed, s = run_myth(analyzer_prog, sol_file, debug, timeout)
        elapsed_str = secs_to_human(elapsed)
        bench_data['elapsed'] = elapsed
        bench_data['elapsed_str'] = elapsed_str

        if s is None:
            print('Benchmark "{}" timed out after {}'.format(test_name, elapsed_str))
            bench_data['elapsed_str'] = elapsed_str
            bench_data['result'] = 'Timed Out'
            timed_out += 1
            continue

        total_time += elapsed
        print(elapsed_str)

        bench_data['execution_returncode'] = s.returncode
        if s.returncode != 0:
            print("mythril invocation:\n\t{}\n failed with return code {}"
                  .format(' '.join(cmd), s.returncode))
            invalid_execution += 1
            bench_data['elapsed_str'] = 'errored'
            bench_data['result'] = 'Errored'
            continue

        data = json.loads(s.stdout)
        if debug:
            pp.pprint(data)
            print("=" * 30)

        if not expected_data:
            unconfigured += 1
            bench_data['result'] = 'Unconfigured'
            print('Benchmark "{}" results not configured, '
                  'so I cannot pass judgement on this'.format(test_name))
            pp.pprint(data)
            print("=" * 30)
            if unconfigured > 5:
                break
        else:
            bench_data['error'] = data['error']
            if data['error']:
                print('Benchmark "{}" errored'.format(test_name))
                bench_data['result'] = 'Unconfigured'
                print(data['error'])
                error_execution += 1
                continue

            data_issues = data['issues']
            if not expected_data['has_bug']:
                if not data_issues:
                    print("No problems found and none expected")
                    bench_data['result'] = 'True Negative'
                    continue
                else:
                    print("Found a problem where none was expected")
                    bench_data['result'] = 'False Positive'
                    error_execution += 1
                    continue

            # The test has a bug, and analysis terminated normally
            # finding some sort of problem. Did we detect the right problem?
            benchmark_success = True
            expected_issues = {(issue['address'], issue['title']): issue
                               for issue in expected_data['issues']}
            bench_data['issues'] = data['issues']
            if len(expected_issues) != len(data_issues):
                print("Expecting to find {} issue(s), got {}"
                      .format(len(expected_issues), len(data_issues)))
                bench_data['result'] = 'Wrong Vulnerability'
                error_execution += 1
                pp.pprint(data_issues)
                print("=" * 30)
                continue

            for issue in data_issues:
                expected_issue = expected_issues.get((issue['address'], issue['title']),
                                                     None)
                if expected_issue:
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
            bench_data['benchmark_success'] = benchmark_success
            bench_data['result'] = 'True Positive'
            if benchmark_success:
                expected += 1
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

    print("\nSummary: {} benchmarks; {} expected results, {} unconfigured, {} aborted abnormally, "
          "{} unexpected results, {} timed out, {} ignored."
          .format(benchmarks, expected, unconfigured, invalid_execution, error_execution,
                  timed_out, ignored_benchmarks))

    total_time_str = secs_to_human(total_time)
    out_data['total_time'] = total_time
    out_data['total_time_str'] = secs_to_human(total_time)
    print("Total elapsed execution time: {}".format(total_time_str))

    for field in """expected unconfigured invalid_execution error_execution
                     timed_out ignored_benchmarks""".split():
        out_data[field] = locals()[field]
    out_data['total_time']= total_time
    out_data['benchmark_count'] = benchmarks

    benchdir = code_root_dir.parent / 'benchdata' / suite
    os.makedirs(benchdir, exist_ok = True)
    with open(benchdir / (analyzer + '.yaml'), 'w') as fp:
        yaml.dump(out_data, fp)


if __name__ == '__main__':
    run_benchmark_suite()
