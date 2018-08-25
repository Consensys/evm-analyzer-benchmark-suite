from .BaseAnalyser import BaseAnalyser, AnalyserError, AnalyserTimeoutError
from .Mythril import Mythril
from .Manticore import Manticore


def get_analyser(name):
    """
    Searches for analyser implementation by its name
    :param name: Name of analyser
    :return: Implementation of BaseAnalyser
    :raises: Exception - No analyser found
    """
    for cls in BaseAnalyser.__subclasses__():
        if cls.get_name().lower() == name.lower():
            return cls

    # Raise exception if no analyser found
    raise Exception("No implementation for analyser '{}' found".format(name))


def list_analysers():
    """
    :return: List of all available analysers
    """
    return [cls.get_name() for cls in BaseAnalyser.__subclasses__()]
