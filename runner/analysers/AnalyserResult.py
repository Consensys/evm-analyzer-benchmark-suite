import pprint

pp = pprint.PrettyPrinter(indent=4)


class AnalyserResult:

    def __init__(self, elapsed, issues=None, error=None):
        """
        Constructor.

        :param elapsed: Test case execution time
        :param issues: List of found issues
        :param error: Error message, if any
        """
        self._elapsed = elapsed
        self._issues = issues
        self._error = error

    @property
    def error(self):
        """
        :return: Error message or None
        """
        return self._error

    @property
    def failed(self):
        """
        :return: True if test execution failed, otherwise Fals
        """
        return self._error is not None and not self._error

    @property
    def elapsed(self):
        """
        :return: Elapsed time
        """
        return self._elapsed

    @property
    def issues(self):
        """
        :return: List of issues
        """
        return self._issues

    def _find_issue(self, issue):
        for i in self._issues:
            # Search by location or address fields
            for key in ('address', 'location',):
                if key in i and i.get(key) != issue.get(key):
                    break
            else:
                return i

    def compare_issues(self, test_name, expected_issues):
        unfound_issues = 0

        for issue in expected_issues:
            # Find same issue by comparing SEARCH_KEYS in both dictionaries
            found_issue = self._find_issue(issue)

            # Print error and continue if expected issue not found
            if not found_issue:
                unfound_issues += 1
                print("Didn't find {} in {}".format(issue, test_name))
                pp.pprint(self.issues)
                continue

            # Verify that found issue is the the expected one by comparing additional fields
            for key in ('title', 'code',):
                if key in issue and issue.get(key) != found_issue.get(key):
                    print("Mismatched issue data in {}".format(test_name))
                    pp.pprint(issue)
                    print('.' * 40)
                    pp.pprint(found_issue)
                    continue

        return unfound_issues
