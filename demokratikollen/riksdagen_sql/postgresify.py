# -*- coding: utf-8 -*-

import sys
import re
import codecs
import string
from itertools import tee
import os

import sqlparse

INSERT_REGEX = (
    r'(?P<cmd>\s*INSERT\s+INTO\s+)'
    r'(?P<names>\S+\s*\([^()]+\))'
    r'(?P<values>\s+VALUES\s*\(.+\);\s*)')

# SQL commands to look for in SQL files
VALID_COMMANDS = ["INSERT"]

# Replacements that should be applied only to table and column names
NAME_REPLACEMENTS = (
    (r"ö(?!(([^']*'){2})*([^']*'))", r"o"), #match ö not followed by odd number of ' (does not handle escaped ')
    (r"å(?!(([^']*'){2})*([^']*'))", r"a"),
    (r"ä(?!(([^']*'){2})*([^']*'))", r"a"),
    (r'\[from\]', r'"from"'))


REMOVE_COL_CORRECTIONS = (
    (r"^\s*INSERT INTO dokument \(hangar_id,dok_id,rm,beteckning,doktyp,typ,subtyp,doktyp,", 7), #if string is matched, remove col 7
    )


def remove_from_list(identifier_list, col_index, filter_func):
    """Remove an item from an ``sqlparse.sql.IdentifierList``.

    The ``IdentifierList`` has a list of tokens. We call a token ``t`` "item" 
    if ``filter_func(t) == True``.

    With this definition of item, this function removes item number 
    ``col_index`` from the identifier list. It also removes the next comma 
    token, if there is any.

    Args:
        identifier_list (sqlparse.sql.IdentifierList): The list to modify.
        col_index (int): The (zero-based) index of the column.
        filter_func (callable): The function determining whether a token
            is an item or not.
    """

    num_cols_found = 0
    col_token_idx = None
    for i, token in enumerate(identifier_list.tokens):
        if filter_func(token):
            num_cols_found += 1

            if num_cols_found == col_index + 1:
                col_token_idx = i
                identifier_list.tokens.remove(token)
                break

    assert col_token_idx is not None

    # Then kill the next comma, if there is any
    for i, token in enumerate(identifier_list.tokens[i:]):
        if str(token) == ',':
            identifier_list.tokens.remove(token)
            break


def remove_col_in_insert(text, col_index):
    '''Removes a column from an SQL INSERT statement.

    Removes the column name and value from an SQL INSERT statement.


    Args:
        text (str): A text string with an SQL INSERT statement.
        col_index (int): The (zero-based) index of the column to be removed.

    Returns:
        A new statement string with the column removed.

    '''
    stmt = sqlparse.parse(text)[0]

    # PART 1: remove the column name

    # table_name (col0, col1, col2, col3)
    into_what = next(t for t in stmt.tokens if isinstance(t, sqlparse.sql.Function))

    # (col0, col1, col2, col3)
    cols_in_parenthesis = into_what.tokens[-1]
    assert isinstance(cols_in_parenthesis, sqlparse.sql.Parenthesis)

    # col0, col1, col2, col3
    cols = cols_in_parenthesis.tokens[1]
    assert isinstance(cols, sqlparse.sql.IdentifierList)

    # Find and kill the identifier
    remove_from_list(cols, col_index, lambda t: isinstance(t, sqlparse.sql.Identifier))


    # PART 2: remove the value

    # Find the last parenthesis -- this should be the values
    # (value0, value1, value2, value3)
    values_in_parenthesis = next(t for t in reversed(stmt.tokens) if isinstance(t, sqlparse.sql.Parenthesis))

    # value0, value1, value2, value3
    values = values_in_parenthesis.tokens[1]
    assert isinstance(values, sqlparse.sql.IdentifierList)

    # Find and kill the value
    remove_from_list(values, col_index, lambda t: t.ttype.split()[1] is sqlparse.tokens.Token.Literal)

    return str(stmt)




def starts_with_command(s):
    """Checks whether a string starts with an SQL command.

    Args:
        s (str): The string to search for valid commands.

    Returns:
        True iff `s.lstrip()` starts with one of the supported commands.
    """
    return any(s.lstrip().startswith(cmd) for cmd in VALID_COMMANDS)


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

def correct_stmt(s):
    """Correct a statement so it (hopefully) works with postgresql"""

    # Make uniform line endings
    s = s.replace('\r\n', '\n')
    s = s.replace('\r', '\n')

    # Get rid of U+FEFF Unicode code point (for some reason present in the middle of some files)
    # (Possible lead: U+FEFF is the Unicode byte order mark...)
    # Anyway, our SQL string probably works best without it anyway, so let's
    # just remove it for now.
    s = s.replace('\uFEFF', '')

    insert_match = re.fullmatch(INSERT_REGEX, s, re.DOTALL)
    if insert_match:
        cmd, names, values = insert_match.groups()

        # Correct name part of INSERT statement 
        for (rx, rep) in NAME_REPLACEMENTS:
            names = re.sub(rx, rep, names)

        # Remove duplicate columns from INSERT statement
        stmt = cmd + names + values
        for (rx, col_index) in REMOVE_COL_CORRECTIONS:
            if re.search(rx, stmt):
                stmt = remove_col_in_insert(stmt, col_index)

        return stmt
    
    else:
        raise RuntimeError("No supported statement was found in the string '" + s + "'")


def main():
    if len(sys.argv) < 2:
        print("Specify file on command line.")
        exit()

    in_path = sys.argv[1]
    dirname, filename = os.path.split(in_path)
    out_path = os.path.join(dirname, 'psql_{}'.format(filename))


    f_in = codecs.open(in_path, 'r', encoding='utf-8')
    f_out = codecs.open(out_path,'w', encoding='utf-8')

    f_out.write('BEGIN;\n')
    for stmt in statements(f_in):
        corrected = correct_stmt(stmt)
        f_out.write(corrected)
    f_out.write('COMMIT;\n')


if __name__ == '__main__':
    main()
