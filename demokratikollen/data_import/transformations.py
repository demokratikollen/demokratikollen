# -*- coding: utf-8 -*-

import re
import itertools
import logging

import sqlparse

logger = logging.getLogger(__name__)

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

def replace_empty_string_with_NULL(s):
    if "VALUES" in s:
        return s.replace("''", "NULL")
    else:
        return s

def fix_empty_values_bet(s):
    return re.sub(",,,'','',''", ",0,0,NULL,NULL,NULL", s)

def fix_empty_times_person(s):
    return re.sub("('[0-9]{4}-[0-9]{2}-[0-9]{2}'),'',(.+,.+\);)", r"\1,NULL,\2", s)

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


def remove_col_in_insert(col_index, stmt_text):
    '''Removes a column from an SQL INSERT statement.

    Removes the column name and value from an SQL INSERT statement.

    Args:
        text (str): An SQL INSERT statement.
        col_index (int): The (zero-based) index of the column to be removed.

    Returns:
        The modified statement.

    '''
    if col_index == 0:
        raise NotImplementedError()


    name = r"[^),]+"
    literal = r"\s*(?:'(?:\\.|''|[^\\'])*'|\s*[\d.]+\s*)\s*"
    regex = (
        "(" +
        r"INSERT\sINTO[^(]+\(" + #INSERT INTO tablename (

        r"(?:{0})".format(name) + # first column
        r"(?:,{0}){{{1}}}".format(name, col_index-2) + # other columns before

        ")" +

        r"(?:,{0})".format(name) + # column to remove

        "(" +

        r"(?:,{0})*".format(name) + # columns after

        r"\)\s*VALUES\s*\(" # ) VALUES (
        
        r"(?:{0})".format(literal) + # first value
        r"(?:,{0}){{{1}}}".format(literal, col_index-2) + # other values before

        ")" +

        r"(?:,{0})".format(literal) + # column to remove

        "(" +

        r"(?:,{0})*".format(literal) + # columns after

        r"\)" +

        ")" 
    )

    match = re.search(regex, stmt_text)
    assert(len(match.groups()) == 3)

    return ''.join(match.groups())



def ifmatch(regex, transformation, otherwise=None):

    def func(stmt):
        stmt = str(stmt)
        if re.search(regex, stmt):
            return transformation(stmt)
        elif otherwise is not None:
            return otherwise(stmt)
        else:
            return stmt

    return func
