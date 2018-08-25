import re
import shutil
from pathlib import Path

from .AnalyserResult import *
from .BaseAnalyser import *


class Manticore(BaseAnalyser):
    """
    Interface to execute Manticore analyser.
    """

    def __init__(self, debug, timeout):
        """ Constructor.
        If you set environment variable MANTICORE, that will be used a the myth CLI command to
        invoke. If that is not set, we run using "manticore".
        :param debug: Whether debug mode is on
        :param timeout: Test case execution timeout
        """
        super().__init__(os.environ.get('MANTICORE', 'manticore'), debug, timeout)

        self._read_version()

    @staticmethod
    def get_name():
        """
        :return: Analyser name
        """
        return 'Manticore'

    @property
    def version(self):
        """
        :return: Manticore version
        """
        return self._version

    def run_test(self, sol_file):
        """
        Execute Manticore on specified solidity file
        Issue format:
            'title': Issue title
            'address': Bytecode offset of failed command
            'lineno': Source code line number
            'code': Part of source code that failed

        :param sol_file: Path to solidity file
        :return: AnalyserResult
        :raises AnalyserError:
        :raises AnalyserTimeoutError:
        """
        res = self._execute('--detect-all', str(sol_file))

        if res['returncode'] != 0:
            raise AnalyserError('Failed to get run Manticore', res['returncode'], res['cmd'])

        output = res['stdout'].decode('utf-8').strip()

        if self.debug:
            pp.pprint(output)
            print('=' * 30)

        # Manticore outputs result path on the last line
        m = re.search('Results in (.+)', output)

        if not m:
            raise AnalyserError('Can not parse output', res['returncode'], res['cmd'])

        report_dir = m.group(1)

        if self.debug:
            print("Manticore report dir: {}".format(report_dir))

        issues = self._parse_report(Path(report_dir))

        return AnalyserResult(res['elapsed'], issues)

    def cleanup(self):
        """ Cleans Manticore output directories """
        super().cleanup()
        # Get list of manticore output directories
        dirs_to_remove = [path for path in Path('.').glob('mcore_*') if path.is_dir()]
        # Clean all of them
        for dir_path in dirs_to_remove:
            if self.debug:
                print("Removing '{}' directory".format(dir_path))

            shutil.rmtree(dir_path)

    def _read_version(self):
        """
        Executes Manticore and reads versions from output
        :return: Manticore version string
        :raises AnalyserError:
        """
        res = self._execute('--version')

        if res['returncode'] != 0:
            raise AnalyserError('Execution failed', res['returncode'], res['cmd'])

        output = res['stdout'].decode('utf-8')

        m = re.search(r'Manticore (.+)', output)
        if not m:
            raise AnalyserError('Can not read Manticore version "{}"'.format(output), cmd=res['cmd'])

        self._version = m.group(1)

    def _parse_snippet(self, snippet):
        """
        Parses Manticore code snipped
        :return: Tuple - line number, code
        :raises AnalyserError:
        """
        # Get only first line and extract line number and code
        first_line = snippet.strip().split('\n')[0]

        m = re.search(r'(\d+)\s+(.*)', first_line)
        if not m:
            raise AnalyserError('Can not parse snippet: "{}"'.format(snippet))

        return m.group(1), m.group(2)

    def _parse_report(self, report_dir):
        """
        Parses generated report
        :param report_dir: Path to generated report directory
        :return: List of issues
        :raises AnalyserError:
        :raises AnalyserTimeoutError:
        """
        # Check for global.findings file that contains all issues that has been found
        report_file = report_dir / 'global.findings'

        if not os.path.exists(report_file):
            return []

        with open(report_file, 'r') as f:
            content = f.read()

        # Each issues ends with empty new line
        findings = content.strip().split('\n\n')

        issues = []
        # Extract necessary fields from each found issue and build issue list
        for finding in findings:
            try:
                title = re.search(r'- (.*) -', finding).group(1)
                address = re.search(r'EVM Program counter: (\d+)', finding).group(1)
                snippet = finding.split(r'Solidity snippet:')[1]

                lineno, code = self._parse_snippet(snippet)

                issues.append({
                    'title': title,
                    'address': int(address),
                    'lineno': int(lineno),
                    'code': code
                })
            except Exception as e:
                raise AnalyserError("Can not parse content of '{}' file. Error: '{}'"
                                    .format(report_file, e))

        return issues
