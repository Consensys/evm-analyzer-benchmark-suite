import os
import re
import subprocess
import time

"""Mythril-related things"""

def get_myth_prog():
    """Return the mythril program name to run. Setting a name inenvironent variable MYTH
    takes precidence of the vanilla name "myth". As a sanity check, try
    running this command with --version to make sure it does something.
    """
    myth_prog = os.environ.get('MYTH', 'myth')
    cmd = [myth_prog, '--version']
    s = subprocess.run(cmd, stdout=subprocess.PIPE)
    if s.returncode != 0:
        print("Failed to get run Mythril with:\n\t{}\n failed with return code {}"
              .format(' '.join(cmd), s.returncode))
        return None
    m = re.search('Mythril version (.+)', s.stdout.decode('utf-8'))
    if m:
        myth_version = m.group(1)
    # FIXME: check version
    return myth_prog, myth_version

def run_myth(myth_prog, sol_file, debug, timeout):
    cmd = [myth_prog, '-x', '-o', 'json', '{}'.format(sol_file)]
    if debug:
        print(' '.join(cmd))
    start = time.time()
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        result = None
    elapsed = (time.time() - start)
    return elapsed, result
