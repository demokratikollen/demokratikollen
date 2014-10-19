# -*- coding: utf-8 -*-

import os.path
import logging
import urllib.request
import urllib.parse

from demokratikollen.data_import.chains import CHAINS

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
root_logger.addHandler(ch)

logger = logging.getLogger(__name__)

# SQL commands to look for in SQL files
VALID_COMMANDS = ['INSERT', 'CREATE']

class CannotCleanException(Exception):
    """An exception for when a data file cannot be cleaned."""
    def __init__(self, filename):
        super(CannotCleanException, self).__init__()
        self.filename = filename
        
    def __str__(self):
        return "The file '{0}' cannot be cleaned.".format(self.path)

def download(urls, out_dir, overwrite=False):
    """Download from URLs to a directory

    Args:
        urls (list of str): The URLs to download from.
        out_dir (str): Path of the directory to download to.
        overwrite (optional, bool): Whether to overwrite existing files.
    """

    try:
        os.makedirs(out_dir)
    except FileExistsError as e:
        pass

    for url in urls:
        url = url.strip()
        urlparts = urllib.parse.urlparse(url)
        filename = os.path.split(urlparts.path)[1]
        out_path = os.path.abspath(os.path.join(out_dir, filename))

        if os.path.exists(out_path) and not overwrite:
            logger.info('Skipping {0} because it already exists.'.format(filename))
            continue
        
        logger.info('Downloading {}.'.format(filename))
        urllib.request.urlretrieve(url, out_path)

def clean(path_in, path_out, overwrite=None):
    """Clean input file and save result to a new file

    Runs a chain of cleaning transformations on all the SQL
    statements found in the input file and saves the result to a new
    file. The chain of transformations is chosen based on the
    file name of the input file.

    Args:
        path_in (str): The path of the input file.
        path_out (str): The path of the output file.
        overwrite (optional, bool): Whether to overwrite existing files.

    """
    path_in = os.path.abspath(path_in)
    dirname, filename_in = os.path.split(path_in)

    if filename_in not in CHAINS:
        raise CannotCleanException(filename_in)

    if os.path.exists(path_out) and not overwrite:
        raise FileExistsError(path_out)
        
    outdir = os.path.dirname(path_out)
    
    try:
        os.makedirs(outdir)
    except FileExistsError as e:
        pass
    
    chain = CHAINS[filename_in]

    with open(path_in, 'r', encoding='utf-8') as f_in, \
            open(path_out, 'w', encoding='utf-8') as f_out:
        
        for s in statements(f_in):
            for func in chain:
                s = func(s)
            
            f_out.write(s + '\n')


def execute_statements(statements, conn):
    """Execute a list of statements with a database connection.

    Executes all the SQL statements and then commits.

    Args:
        statements (iterable of str): The list of statements.
        conn (psycopg2.Connection): The postgresql connection to use.
    """
    
    with conn.cursor() as cur:
        count = 0
        for stmt in statements:
            cur.execute(stmt)
            count += 1

        logger.info('Executed {0} statement(s). Commiting.'.format(count))
        conn.commit()


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
