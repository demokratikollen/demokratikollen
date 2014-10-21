# -*- coding: utf-8 -*-

from functools import partial
import demokratikollen.data_import.transformations as tr

CHAINS = {}
CHAINS['test.sql'] = (
    tr.correct_line_endings,
    tr.remove_funky_characters,
    tr.parse_stmt,
    tr.fix_names,
    tr.ifmatch((
        r"^\s*INSERT INTO dokument "
        r"\(hangar_id,dok_id,rm,beteckning,doktyp,typ,subtyp,doktyp,"),
        partial(tr.remove_col_in_insert, 7)),
    str
    )

CHAINS['votering-201314.sql'] = \
CHAINS['votering-201213.sql'] = \
CHAINS['votering-201112.sql'] = \
CHAINS['votering-201011.sql'] = \
CHAINS['votering-200910.sql'] = \
CHAINS['votering-200809.sql'] = \
CHAINS['votering-200708.sql'] = \
CHAINS['votering-200607.sql'] = \
CHAINS['votering-200506.sql'] = \
CHAINS['votering-200405.sql'] = \
CHAINS['votering-200304.sql'] = \
CHAINS['votering-200203.sql'] = \
CHAINS['bet-2010-2013.sql'] = \
CHAINS['bet-2006-2009.sql'] = \
CHAINS['bet-2002-2005.sql'] = \
CHAINS['mot-2010-2013.sql'] = \
CHAINS['mot-2006-2009.sql'] = \
CHAINS['mot-2002-2005.sql'] = \
CHAINS['prop-2010-2013.sql'] = (
    tr.correct_line_endings,
    tr.remove_funky_characters
    )

CHAINS['person.sql'] = (
    tr.correct_line_endings,
    tr.remove_funky_characters,
    tr.parse_stmt,
    tr.fix_names,
    str
    )
