# -*- coding: utf-8 -*-

import re
import itertools

import sqlparse


def correct_line_endings(s):
    # Make uniform line endings
    s = s.replace('\r\n', '\n')
    s = s.replace('\r', '\n')

    return s

def remove_funky_characters(s):
    # Get rid of U+FEFF Unicode code point (for some reason present in the middle of some files)
    # (Possible lead: U+FEFF is the Unicode byte order mark...)
    # Anyway, our SQL string probably works best without it anyway, so let's
    # just remove it for now.
    s = s.replace('\uFEFF', '')

    return s

def parse_stmt(text):
    return sqlparse.parse(text)[0]

def _flatten(l):
    return itertools.chain(*l)

def _get_leaves(sql):
    if hasattr(sql, 'tokens'):
        return _flatten(map(_get_leaves, sql.tokens))
    else:
        return [sql]

def fix_names(stmt):
    # Replacements that should be applied only to table and column names
    replacements = (
        ('ö', 'o'),
        ("å", 'a'),
        ('ä', 'a'),
        (r'\[([^\[\]]+)\]', r'"\1"'))

    # table_name (col0, col1, col2, col3)
    into_what = next(t for t in stmt.tokens if isinstance(t, sqlparse.sql.Function))

    is_name = lambda t: t.ttype.split()[1] is sqlparse.tokens.Token.Name

    # Get all the table and column name tokens
    names = filter(is_name, _get_leaves(into_what))

    for name in names:
        for (rx, repl) in replacements:
            name.value = re.sub(rx, repl, name.value)

    return stmt


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


def remove_col_in_insert(col_index, stmt):
    '''Removes a column from an SQL INSERT statement.

    Removes the column name and value from an SQL INSERT statement.

    Args:
        text (sqlparse.sql.Statement): A parsed SQL INSERT statement.
        col_index (int): The (zero-based) index of the column to be removed.

    Returns:
        The modified statement.

    '''
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
    values_in_parenthesis = next(
        t for t in reversed(stmt.tokens) if isinstance(t, sqlparse.sql.Parenthesis))

    # value0, value1, value2, value3
    values = values_in_parenthesis.tokens[1]
    assert isinstance(values, sqlparse.sql.IdentifierList)

    # Find and kill the value
    remove_from_list(
        values,
        col_index,
        lambda t: t.ttype.split()[1] is sqlparse.tokens.Token.Literal)

    return stmt

def ifmatch(regex, transformation, otherwise=None):

    def func(stmt):
        stmt_text = str(stmt)
        if re.search(regex, stmt_text):
            return transformation(stmt)
        elif otherwise is not None:
            return otherwise(stmt)
        else:
            return stmt

    return func
