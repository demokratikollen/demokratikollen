# -*- coding: utf-8 -*-

from functools import partial
import data_import.transformations as tr

CHAINS = {
    'test.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters,
        tr.parse_stmt,
        tr.fix_names,
        tr.ifmatch((
            r"^\s*INSERT INTO dokument "
            r"\(hangar_id,dok_id,rm,beteckning,doktyp,typ,subtyp,doktyp,"),
            partial(tr.remove_col_in_insert, 7)),
        str
        ),

    'bet-2010-2013.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters
        ),

    'votering-201314.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters
        ),

    'votering-201213.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters
        ),

    'person.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters,
        tr.parse_stmt,
        tr.fix_names,
        str
        ),

    'votering-201213.sql': (
        tr.correct_line_endings,
        tr.remove_funky_characters
        )
}
