# -*- coding: utf-8 -*-

import os.path
import logging

from data_import.chains import CHAINS

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
root_logger.addHandler(ch)

logger = logging.getLogger(__name__)

# SQL commands to look for in SQL files
VALID_COMMANDS = ["INSERT"]

def main():
    pass

def clean(path_in, prefix_out):
    path_in = os.path.abspath(path_in)
    dirname, filename_in = os.path.split(path_in)
    path_out = os.path.join(dirname, prefix_out + filename_in)
    
    chain = CHAINS[filename_in]

    with open(path_in, 'r', encoding='utf-8') as f_in, \
            open(path_out, 'w', encoding='utf-8') as f_out:
        
        f_out.write('BEGIN;\n')
        for s in statements(f_in):
            for func in chain:
                logger.debug('Running {0}'.format(func.__name__))
                s = func(s)
            
            f_out.write(s + '\n')
            
        f_out.write('COMMIT;')


def statements(f):
    """Returns a generator with statements found in a file-like object.

    Functionality builds on two important assumptions:

    *   The file `f` must contains only SQL statements, and only 
        those supported by :func:`starts_with_command`.
    *   Each statement starts on a new line.

    Args:
        f (file-like object): The source of statements.

    Returns:
        A generator object, yielding strings with statements.
    """
    in_stmt = False
    lines = []

    for line in f:
        is_stmt_start = starts_with_command(line)
        
        if in_stmt and is_stmt_start:
            yield ''.join(lines)
            lines = []

        in_stmt = in_stmt or is_stmt_start

        if in_stmt:
            lines.append(line)

    if in_stmt:
        yield ''.join(lines)


def starts_with_command(s):
    """Checks whether a string starts with an SQL command.

    Args:
        s (str): The string to search for valid commands.

    Returns:
        True if `s.lstrip()` starts with one of the supported commands,
            False otherwise.
    """
    return any(s.lstrip().startswith(cmd) for cmd in VALID_COMMANDS)



if __name__ == '__main__':
    main()