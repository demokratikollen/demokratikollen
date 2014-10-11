import sys
from re import sub
import codecs
import string
from itertools import tee
import os

regexes = [
(r"ö(?!(([^']*'){2})*([^']*'))",r"o"), #match ö not followed by odd number of ' (does not handle escaped ')
(r"å(?!(([^']*'){2})*([^']*'))",r"a"),
(r"ä(?!(([^']*'){2})*([^']*'))",r"a"),
(r'\[from\]', r'"from"')
]

# Statements to look for in SQL files (any others?)
VALID_STATEMENTS = ["INSERT","CREATE"]

def pairwise(iterable):
    """Recipe from itertools
    s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def statements(f):
    def is_stmt_line(line):
        return any(line.lstrip().startswith(stmt) for stmt in VALID_STATEMENTS)
    lines = []
    statement_started = False
    for line,next_line in pairwise(f):
        if not statement_started:
            if is_stmt_line(line):
                statement_started = True

        if statement_started:
            lines.append(line)
            if is_stmt_line(next_line):
                yield ''.join(lines).strip()
                lines=[]
                statement_started=False

    if statement_started:
        yield ''.join(lines).strip()



def convert(s):
    t = s.strip()

    if not t.startswith('(') and not t.startswith('INSERT') and not t.startswith('VALUES'):
        return None

    for (rx, rep) in regexes:
        t = sub(rx, rep, t)

    t = t.replace('\r\n', '\n')
    t = t.replace('\r', '\n')
    return t

def main():
    if len(sys.argv) < 2:
        print("Specify file on command line.")
        exit()

    in_path = sys.argv[1]
    dirname, filename = os.path.split(in_path)
    out_path = os.path.join(dirname, 'psql_{}'.format(filename))

    f_in = codecs.open(in_path, 'r', encoding='utf-8')#open(filename, 'r')

    for statement in statements(f_in):
        print("Statement:")
        print(statement)

    exit()
    f_out = codecs.open(out_path,'w', encoding='utf-8') #open('psql_{}'.format(filename),'w')

    f_out.write('BEGIN;\n')
    for line in f_in:
        converted = convert(line)
        if not converted is None:
            f_out.write(converted)
            f_out.write('\n')
    f_out.write('COMMIT;\n')


if __name__ == '__main__':
    main()
