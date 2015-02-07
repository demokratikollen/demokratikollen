# coding=utf-8

import datetime as dt

PARTY_LEADERS = {}

# N.B. Many dates are unclear, but years should be right at least.


PARTY_LEADERS["sd"] = [
	{ "start": "1992-01-01", "end": "1995-03-05", "name": "Anders Klarström"},
	{ "start": "1995-03-05", "end": "2005-05-07", "name": "Mikael Jansson"},
	{ "start": "2005-05-07", "name": "Jimmie Åkesson"}]


PARTY_LEADERS["c"] = [
    { "start": "1971-01-01", "end": "1985-10-01", "name": "Thorbjörn Fälldin"},
    { "start": "1985-10-01", "end": "1987-06-01", "name": "Karin Söder"},
    { "start": "1987-06-01", "end": "1998-06-01", "name": "Olof Johansson"},
    { "start": "1998-06-01", "end": "2001-01-19", "name": "Lennart Daléus"},
    { "start": "2001-03-19", "end": "2011-09-23", "name": "Maud Olofsson"},
    { "start": "2011-09-23", "name": "Annie Lööf"}]


PARTY_LEADERS["s"] = [
    { "start": "1969-10-14", "end": "1986-02-28", "name": "Olof Palme" },
    { "start": "1986-03-13", "end": "1996-03-22", "name": "Ingvar Carlsson" },
    { "start": "1996-03-22", "end": "2007-03-17", "name": "Göran Persson" },
    { "start": "2007-03-17", "end": "2011-03-25", "name": "Mona Sahlin" },
    { "start": "2011-03-25", "end": "2012-01-21", "name": "Håkan Juholt" },
    { "start": "2012-01-27", "name": "Stefan Löfven" }]

PARTY_LEADERS["m"] = [
    { "start": "1970-09-01", "end": "1986-08-23", "name": "Gösta Bohman" },
    { "start": "1981-09-01", "end": "1986-08-23", "name": "Ulf Adelsohn" },
    { "start": "1986-08-23", "end": "1999-09-04", "name": "Carl Bildt" },
    { "start": "1999-09-04", "end": "2003-10-25", "name": "Bo Lundgren" },
    { "start": "2003-10-25", "end": "2015-01-10", "name": "Fredrik Reinfeldt" },
    { "start": "2015-01-10", "name": "Anna Kinberg Batra" }]

PARTY_LEADERS["kd"] = [
    { "start": "1971-04-01", "end": "2004-04-03", "name": "Alf Svensson" },
    { "start": "2004-04-03", "name": "Göran Hägglund" }]

PARTY_LEADERS["v"] = [
    { "start": "1975-02-01", "end": "1993-02-01", "name": "Lars Werner"},
    { "start": "1993-02-01", "end": "2003-01-26", "name": "Gudrun Schyman"},
    { "start": "2003-02-07", "end": "2004-02-20", "name": "Ulla Hoffmann"},
    { "start": "2004-02-20", "end": "2012-01-06", "name": "Lars Ohly" },
    { "start": "2012-01-06", "name": "Jonas Sjöstedt" }]

PARTY_LEADERS["mp"] = [
    { "start": "1984-06-03", "end": "1985-09-01", "name": "Per Gahrton, Ragnhild Pohanka" },
    { "start": "1985-09-01", "end": "1986-05-03", "name": "Ragnhild Pohanka, Birger Schlaug" },
    { "start": "1986-05-03", "end": "1988-04-04", "name": "Eva Goës, Birger Schlaug" },
    { "start": "1988-04-04", "end": "1990-06-16", "name": "Fiona Björling, Anders Nordin" },
    { "start": "1990-06-16", "end": "1992-04-20", "name": "Jan Axelsson, Margareta Gisselberg" },
    { "start": "1992-04-20", "end": "1999-05-15", "name": "Marianne Samuelsson, Birger Schlaug" },
    { "start": "1999-05-15", "end": "2000-06-04", "name": "Lotta Hedström, Birger Schlaug" },
    { "start": "2000-06-04", "end": "2002-05-12", "name": "Matz Hammarström, Lotta Hedström" },
    { "start": "2002-05-12", "end": "2011-05-21", "name": "Peter Eriksson, Maria Wetterstrand" },
    { "start": "2011-05-21", "name": "Gustav Fridolin, Åsa Romson" }]

PARTY_LEADERS["fp"] = [
    { "start": "1969-01-01", "end": "1975-11-07", "name": "Gunnar Helén" },
    { "start": "1975-11-07", "end": "1978-03-04", "name": "Per Ahlmark" },
    { "start": "1978-03-04", "end": "1983-10-01", "name": "Olof Ullsten" },
    { "start": "1983-10-01", "end": "1995-02-04", "name": "Bengt Westerberg" },
    { "start": "1995-02-04", "end": "1997-03-15", "name": "Maria Leissner" },
    { "start": "1997-03-15", "end": "2007-09-07", "name": "Lars Leijonborg" },
    { "start": "2007-09-07", "name": "Jan Björklund" }]