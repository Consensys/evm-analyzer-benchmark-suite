import os
import time
import signal
from subprocess import Popen, PIPE
from threading import Timer


class AnalyserError(Exception):
    """ Error thrown where analyser failed to execute given command
        or returned unexpected output
    """
    def __init__(self, message, returncode=0, cmd=''):
        super().__init__(message)
        self.returncode = returncode
        self.cmd = cmd


class AnalyserTimeoutError(Exception):
    """ Error thrown when analyser process execution took too long """
    def __init__(self, elapsed):
        self.elapsed = elapsed


class BaseAnalyser:
    """
    Abstract class which must be inherited by every analyser implementation
    """
    def __init__(self, program, debug, timeout):
        """
        Base constructor

        :param program: Path to analyser executable file
        :param debug: Whether to write debug output
        :param timeout: Test case execution timeout
        """
        self._program = program
        self._timeout = timeout
        self._debug = debug

    def _execute(self, *args):
        """
        Executes specified program with given arguments

        :param *args: Arguments
        :return: Tuple - return code, elapsed time, stdout, stderr, executed command
        :raises AnalyserTimeoutError: Process took more than timeout seconds
        """
        cmd = [self._program, *args]
        # subprocess timeout does not work with processes that starts multiple child processes
        # therefore, as a workaround there is a need to use Popen() and kill process group instead
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid)

        timer = Timer(self.timeout, lambda: os.killpg(os.getpgid(proc.pid), signal.SIGTERM))
        start = time.time()
        try:
            timer.start()
            stdout, stderr = proc.communicate()
        finally:
            timer.cancel()
            elapsed = (time.time() - start)

        # Raise timeout exception if process was not killed by timer
        if proc.returncode == -15 and not timer.is_alive():
            raise AnalyserTimeoutError(elapsed)

        return {
            'returncode': proc.returncode,
            'elapsed': elapsed,
            'stdout': stdout,
            'stderr': stderr,
            'cmd': ' '.join(cmd)
        }

    @property
    def debug(self):
        """
        :return: Whether the debug mode is on
        """
        return self._debug

    @property
    def timeout(self):
        """
        :return: Execution timeout
        """
        return self._timeout

    def run_test(self, sol_file):
        """
        Run analyser on specified solidity file

        :param sol_file: Path to solidity file
        :return: AnalyserResult
        """
        raise NotImplementedError("run_test method is not implemented")

    def cleanup(self):
        """
        Performs cleanup after all tests are executed or when program exited
        Optional for implementation
        """
        pass

    @staticmethod
    def get_name():
        """
        :return: Analyser name
        """
        raise NotImplementedError("analyser getter not implemented")

    @property
    def version(self):
        """
        :return: Analyser version
        """
        raise NotImplementedError("version getter is not implemented")
