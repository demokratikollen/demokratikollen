# -*- coding: utf-8 -*-

import sys
from re import sub
import codecs
regexes = [
(r"ö(?!(([^']*'){2})*([^']*'))",r"o"), #match ö not followed by odd number of ' (does not handle escaped ')
(r"å(?!(([^']*'){2})*([^']*'))",r"a"),
(r"ä(?!(([^']*'){2})*([^']*'))",r"a"),
(r'\[from\]', r'"from"')
]

def convert(s):
	t = s
	for (rx, rep) in regexes:
		t = sub(rx, rep, t)

	return t

def main():
	if len(sys.argv) < 2:
		print "Specify file on command line."
		exit()

	filename = sys.argv[1]

	f_in = codecs.open(filename, 'r',encoding='utf-8')#open(filename, 'r')
	f_out = codecs.open('psql_{}'.format(filename),'w', encoding='utf-8') #open('psql_{}'.format(filename),'w')
	for line in f_in:
		converted = convert(line)
		f_out.write(converted)



if __name__ == '__main__':
	main()