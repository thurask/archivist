import os
import argparse


def file_exists(file):
    """
    Check if file exists. Used for parsing file inputs from command line.
    :param file: \\path\\to\\file.ext
    :type file: str
    """
    if not os.path.exists(file):
        raise argparse.ArgumentError("{0} does not exist".format(file))
    return file
