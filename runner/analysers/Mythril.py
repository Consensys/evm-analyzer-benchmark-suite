import re
import json

from .AnalyserResult import *
from .BaseAnalyser import *


class Mythril(BaseAnalyser):
    """
    Interface to execute Mythril analyser.
    """

    def __init__(self, debug, timeout):
        """ Constructor.
        If you set environment variable MYTH, that will be used a the myth CLI command to
        invoke. If that is not set, we run using "myth".
        :param debug: Whether debug mode is on
        :param timeout: Test case execution timeout
        """
        super().__init__(os.environ.get('MYTH', 'myth'), debug, timeout)

        self._read_version()

    @staticmethod
    def get_name():
        return 'Mythril'

    @property
    def version(self):
        return self._version

    def _read_version(self):
        """
        Execute Mythril and set application version

        :raise AnalyserException:
        """
        res = self._execute('--version')

        if res['returncode'] != 0:
            raise AnalyserError('Execution failed', res['returncode'], res['cmd'])

        output = res['stdout'].decode('utf-8')

        m = re.search(r'Mythril version (.+)', output)
        if not m:
            raise AnalyserError("Can not read Mythril version '{}'".format(output))

        self._version = m.group(1)

    def run_test(self, sol_file):
        """
        Execute Mythril on specified solidity file.
        Issue format:
            'title': Issue title
            'address': Bytecode offset of failed command
            'code': Part of source code that failed

        :param sol_file: Path to solidity file
        :return: AnalyserResult
        :raises AnalyserError:
        :raises AnalyserTimeoutError:
        """
        res = self._execute('-x', '-o', 'json', str(sol_file))

        if res['returncode'] != 0:
            AnalyserError("Failed to get run Mythril", res['returncode'], res['cmd'])

        data = None
        try:
            data = json.loads(res['stdout'])
        except Exception as e:
            AnalyserError("Can not parse output: '{}'".format(str(e)), res['returncode'], res['cmd'])

        if self.debug:
            pp.pprint(data)
            print('=' * 30)

        return AnalyserResult(res['elapsed'], data['issues'], data['error'])
