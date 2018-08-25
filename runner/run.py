#!/usr/bin/env python
"""
top-level CLI to run benchmarks
"""

import os, sys, time
import yaml
import click
import pprint
from pathlib import Path
from glob import glob
from analysers import get_analyser, list_analysers, AnalyserError, AnalyserTimeoutError

pp = pprint.PrettyPrinter(indent=4)

code_root_dir = Path(__file__).parent.resolve()
project_root_dir = code_root_dir.parent

# Make relative loading work without relative import, which
# doesn't work with main programs
sys.path.insert(0, code_root_dir)


# Maximum time, in seconds, that we allow the analyzer to
# take in analyzing a benchmark.
DEFAULT_TIMEOUT = 7.0


def secs_to_human(elapsed):
    """
    Format `elapsed` into a human-readable string with hours, minutes and seconds
    :param elapsed: Milliseconds
    :return: Human readable time string
    """
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
    """
    Reads benchmark configuration
    :param project_root_dir: Project root directory
    :param suite_name: Name of test suite
    :param analyzer: Name of analyser
    :param debug: Whether debug is on
    :return: Benchmark configuration
    """
    testsuite_conf_path = project_root_dir / 'benchconf' / "{}.yaml".format(suite_name)
    if not testsuite_conf_path.exists():
        return {}
    testsuite_conf = yaml.load(open(testsuite_conf_path, 'r'))
    analyzer_conf_path = project_root_dir / 'benchconf' / "{}-{}.yaml".format(suite_name, analyzer)
    analyzer_conf = yaml.load(open(analyzer_conf_path, 'r'))
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
    """
    Get the list of benchmark files
    :param root_dir: Project root directory
    :param suite_name: Name of test suite
    :param benchmark_subdir: Benchmark subdirectory if any
    :return: Sorted list of benchmark files
    """
    testsuite_benchdir = root_dir.parent / 'benchmarks' / suite_name / benchmark_subdir
    os.chdir(testsuite_benchdir)
    return sorted(glob('**/*.sol', recursive=True))


def run_benchmark_suite(analyser, suite, verbose, debug, timeout, files):
    """ Run an analyzer (like Mythril) on a benchmark suite.
    :param analyser: BaseAnalyser child instance
    :param suite: Name of test suite
    :param verbose: Verbosity
    :param debug: Whether debug is on
    :param timeout: Test execution timeout
    :param files: When True, prints list of solidity files and exits
    :return:
    """
    print("Using {} {}".format(analyser.get_name(), analyser.version))

    testsuite_conf = get_benchmark_yaml(project_root_dir, suite, analyser.get_name(), debug)
    benchmark_files = gather_benchmark_files(code_root_dir, suite,
                                             testsuite_conf['benchmark_subdir'])

    out_data = {
        'analyzer': analyser.get_name(),
        'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'version': analyser.version,
        'suite': testsuite_conf['suite'],
    }

    for field in 'benchmark_subdir benchmark_link benchmark_url_dir'.split():
        out_data[field] = testsuite_conf[field]

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

    for sol_file in benchmark_files:
        benchmarks += 1

        print('-' * 40)
        print("Checking {}".format(sol_file))

        # Generate path to solidity file
        sol_path = Path(sol_file)
        test_name = str(sol_path.parent / sol_path.stem)

        # Read expected data and initialize output variables
        expected_data = testsuite_conf.get(test_name, None)
        bench_data = out_data['benchmarks'][test_name] = {}
        bench_data['bug_type'] = expected_data.get('bug_type', 'Unknown')
        bench_data['expected_data'] = expected_data

        if expected_data:
            run_time = expected_data.get('run_time', timeout)
            if expected_data.get('ignore', None):
                # Test case ignored
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

        try:
            res = analyser.run_test(sol_file)
        except AnalyserError as e:
            print("{} invocation:\n\t{}\n failed with return code {}.\n\tError: {}"
                  .format(analyser.get_name(), e.cmd, e.returncode, str(e)))
            invalid_execution += 1
            bench_data['elapsed_str'] = 'errored'
            bench_data['result'] = 'Errored'
            bench_data['execution_returncode'] = e.returncode

            continue
        except AnalyserTimeoutError as e:
            elapsed_str = secs_to_human(e.elapsed)
            print('Benchmark "{}" timed out after {}'.format(test_name, elapsed_str))
            timed_out += 1
            bench_data['elapsed'] = e.elapsed
            bench_data['elapsed_str'] = elapsed_str
            bench_data['execution_returncode'] = 0
            bench_data['result'] = 'Timed Out'

            continue

        elapsed_str = secs_to_human(res.elapsed)
        bench_data['elapsed'] = res.elapsed
        bench_data['elapsed_str'] = elapsed_str
        bench_data['execution_returncode'] = 0

        total_time += res.elapsed
        print(elapsed_str)

        if not expected_data:
            unconfigured += 1
            bench_data['result'] = 'Unconfigured'
            print('Benchmark "{}" results not configured, '
                  'so I cannot pass judgement on this'.format(test_name))
            pp.pprint(res.issues)
            print("=" * 30)
            if unconfigured > 5:
                break

            continue

        if res.failed:
            print('Benchmark "{}" errored'.format(test_name))
            bench_data['result'] = 'Unconfigured'
            bench_data['error'] = res.error
            print(bench_data['error'])
            error_execution += 1

            continue

        bench_data['issues'] = res.issues

        if not res.issues:
            if not expected_data['has_bug']:
                print("No problems found and none expected")
                bench_data['result'] = 'True Negative'
                expected += 1

                continue
            else:
                print("No problems found when issues were expected")
                bench_data['result'] = 'False Negative'
                error_execution += 1

                continue
        else:
            if not expected_data['has_bug']:
                print("Found a problem where none was expected")
                bench_data['result'] = 'False Positive'
                error_execution += 1

                continue

        # The test has a bug, and analysis terminated normally
        # finding some sort of problem. Did we detect the right problem?
        expected_issues = expected_data.get('issues', [])

        if len(expected_issues) != len(res.issues):
            print("Expecting to find {} issue(s), got {}"
                  .format(len(expected_issues), len(res.issues)))
            bench_data['result'] = 'Wrong Vulnerability'
            error_execution += 1
            pp.pprint(res.issues)
            print("=" * 30)

            continue

        unfound_issues = res.compare_issues(test_name, expected_issues)
        benchmark_success = unfound_issues == 0

        bench_data['benchmark_success'] = benchmark_success
        bench_data['result'] = 'True Positive'

        if benchmark_success:
            expected += 1
            print('Benchmark "{}" checks out'.format(test_name))
            if verbose:
                for num, issue in enumerate(res.issues):
                    print("  Issue {1}. {2} {0[title]} "
                          "at address {0[address]}:\n\t{0[code]}"
                          .format(issue, bench_data['bug_type'], num))

    print('-' * 40)

    print("\nSummary: {} benchmarks; {} expected results, {} unconfigured, {} aborted abnormally, "
          "{} unexpected results, {} timed out, {} ignored.\n"
          .format(benchmarks, expected, unconfigured, invalid_execution, error_execution,
                  timed_out, ignored_benchmarks))

    total_time_str = secs_to_human(total_time)
    out_data['total_time'] = total_time
    out_data['total_time_str'] = secs_to_human(total_time)
    print("Total elapsed execution time: {}".format(total_time_str))

    for field in """expected unconfigured invalid_execution error_execution
                         timed_out ignored_benchmarks""".split():
        out_data[field] = locals()[field]
    out_data['total_time'] = total_time
    out_data['benchmark_count'] = benchmarks

    benchdir = code_root_dir.parent / 'benchdata' / suite
    os.makedirs(benchdir, exist_ok=True)
    with open(benchdir / (analyser.get_name() + '.yaml'), 'w') as fp:
        yaml.dump(out_data, fp)


# TODO add json config lint function?
@click.command()
@click.option('--suite', '-s', type=click.Choice(['Suhabe', 'nssc']),
              default='Suhabe',
              help="Benchmark suite to run; "
              "nscc is an abbreviation for not-so-smart-contracts.")
@click.option('--analyser', '-a', type=click.Choice(list_analysers() + ['all']),
              default='all',
              help="Analyser tool to benchmark")
@click.option('--verbose', '-v', count=True,
              help="More verbose output; use twice for the most verbose output.")
@click.option('--timeout', '-t', type=float,
              default=DEFAULT_TIMEOUT,
              help="Maximum time allowed on any single benchmark.")
@click.option('--files/--no-files', default=False,
              help="List files in benchmark and exit.")
def main(suite, analyser, verbose, timeout, files):
    debug = verbose == 2

    analyser_instance = None
    analysers = list_analysers() if analyser == 'all' else [analyser]

    for tool in analysers:
        try:
            analyser_cls = get_analyser(tool)
            analyser_instance = analyser_cls(debug, timeout)
            run_benchmark_suite(analyser_instance, suite, verbose, debug, timeout, files)
        except AnalyserError as e:
            print("Failed to initialize analyser. Program '{}' failed with {} error code".format(e.cmd, e.returncode))
            sys.exit(1)
        finally:
            if analyser_instance:
                print("{} analyser finished. Cleaning up".format(analyser_instance.get_name()))
                analyser_instance.cleanup()


if __name__ == '__main__':
    main()
