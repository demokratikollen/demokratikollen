
CREATE TABLE dokument (
hangar_id integer,
dok_id varchar(255),
rm varchar(255),
beteckning varchar(255),
doktyp varchar(255),
typ varchar(255),
subtyp varchar(255),
tempbeteckning varchar(255),
organ varchar(255),
mottagare varchar(255),
nummer integer,
slutnummer integer,
datum timestamp,
systemdatum timestamp,
publicerad timestamp,
titel varchar(255),
subtitel varchar(255),
status varchar(255),
htmlformat varchar(255),
relaterat_id varchar(255),
source varchar(255),
sourceid varchar(255),
dokument_url_text varchar(255),
dokument_url_html varchar(255),
dokumentstatus_url_xml varchar(255),
utskottsforslag_url_xml varchar(255),
html text
);

 
CREATE TABLE dokutskottsforslag (
rm varchar(255),
bet varchar(255),
punkt integer,
beteckning varchar(255),
rubrik varchar(255),
forslag varchar(255),
forslag_del2 varchar(255),
beslutstyp varchar(255),
beslut varchar(255),
motforslag_nummer integer,
motforslag_partier varchar(255),
votering_id varchar(255),
votering_sammanfattning_html varchar(255),
votering_ledamot_url_xml varchar(255),
vinnare varchar(255)
);

 
CREATE TABLE dokmotforslag (
nummer integer,
rubrik varchar(255),
forslag varchar(255),
partier varchar(255),
typ varchar(255),
utskottsforslag_punkt integer,
id varchar(255)
);

 
CREATE TABLE dokaktivitet (
hangar_id integer,
kod varchar(255),
namn varchar(255),
datum timestamp,
status varchar(255),
ordning varchar(255),
process varchar(255)
);

 
CREATE TABLE dokintressent (
hangar_id integer,
intressent_id varchar(255),
namn varchar(255),
partibet varchar(255),
ordning integer,
roll varchar(255)
);

 
CREATE TABLE dokforslag (
hangar_id integer,
nummer integer,
beteckning varchar(255),
lydelse varchar(255),
lydelse2 varchar(255),
utskottet varchar(255),
kammaren varchar(255),
behandlas_i varchar(255),
kammarbeslutstyp varchar(255)
);
 
 
 
CREATE TABLE dokuppgift (
hangar_id integer,
kod varchar(255),
namn varchar(255),
text text
);

 
CREATE TABLE dokbilaga (
hangar_id integer,
dok_id varchar(255),
titel varchar(255),
subtitel varchar(255),
filnamn varchar(255),
filstorlek integer,
filtyp varchar(255),
fil_url varchar(255)
);

 
CREATE TABLE dokreferens (
hangar_id integer,
referenstyp varchar(255),
uppgift varchar(255),
ref_dok_id varchar(255),
ref_dok_typ varchar(255),
ref_dok_rm varchar(255),
ref_dok_bet varchar(255),
ref_dok_titel varchar(255),
ref_dok_subtitel varchar(255)
);

 
CREATE TABLE debatt (
hangar_id integer,
video_id varchar(255),
video_url varchar(255),
tumnagel varchar(255),
anf_video_id varchar(255),
anf_hangar_id integer,
anf_sekunder integer,
anf_klockslag varchar(255),
datumtid timestamp,
talare varchar(255),
anf_datum timestamp,
anf_typ varchar(255),
anf_text varchar(255),
anf_beteckning varchar(255),
anf_nummer varchar(255),
intressent_id varchar(255),
parti varchar(255),
anf_rm varchar(255)
);

 
 
CREATE TABLE votering (
rm varchar(255), 
beteckning varchar(255),
hangar_id integer,
votering_id varchar(255),
punkt integer,
namn varchar(255),
intressent_id varchar(255),
parti varchar(255),
valkrets varchar(255),
valkretsnummer integer,
iort varchar(255),
rost varchar(255),
avser varchar(255),
votering varchar(255),
banknummer integer,
fornamn varchar(255),
efternamn varchar(255),
kon varchar(255),
fodd integer,
datum timestamp
);



CREATE TABLE anforande (
pk integer,
dok_id varchar(50),
dok_titel varchar(255),
dok_hangar_id integer,
dok_rm varchar(20),
dok_nummer integer,
dok_datum timestamp,
avsnittsrubrik varchar(255),
kammaraktivitet varchar(250),
justerat char(1),
anf_id varchar(50),
anf_nummer integer,
talare varchar(250),
rel_dok_id varchar(50),
parti varchar(50),
lydelse text,
intressent_id varchar(50),
intressent_hangar_id integer,
replik char(1),
systemdatum timestamp,
kalla varchar(50),
anf_hangar_id integer,
rel_dok_hangar_id int
);



CREATE TABLE person (
id integer,
hangar_id integer,
intressent_id varchar(20),
kontrollsumma varchar(50),
fodd_ar smallint,
fodd timestamp,
avliden timestamp,
kon varchar(6),
fornamn varchar(50),
efternamn varchar(50),
tilltalsnamn varchar(50),
sorteringsnamn varchar(80),
iort varchar(40),
parti varchar(40),
valkrets varchar(50),
banknummer integer,
invalsordning integer,
status varchar(100),
kalla varchar(20),
kalla_id varchar(40),
statsrad varchar(50),
"timestamp" timestamp,
personid int
);




CREATE TABLE personuppdrag (
id integer,
organ_kod varchar(20),
hangar_id integer,
intressent_id varchar(20),
ordningsnummer integer,
roll_kod varchar(40),
status varchar(20),
typ varchar(20),
"from" timestamp,
tom timestamp,
kalla varchar(30),
kalla_id varchar(40),
uppgift varchar(500)
);



CREATE TABLE personuppgift (
id integer,
hangar_id integer,
intressent_id varchar(50),
uppgift_kod varchar(50),
uppgift text,
kalla varchar(50),
kalla_id varchar(50),
uppgift_typ varchar(50)
);



CREATE TABLE planering (
nyckel integer,
id varchar(50),
rm varchar(12),
typ varchar(40),
dokserie_id char(2),
subtyp varchar(40),
bet varchar(40),
tempbet varchar(40),
intressent varchar(80),
nummer integer,
slutnummer integer,
datum timestamp,
publicerad timestamp,
status varchar(40),
titel varchar(300),
subtitel varchar(255),
html text,
toc text,
refcss varchar(66),
url varchar(100),
uppdaterad timestamp,
storlek integer,
source varchar(20),
wn_expires timestamp,
wn_cachekey varchar(50),
wn_status varchar(20),
wn_checksum varchar(40),
wn_nid integer,
wn_RawUrl varchar(255),
wn_SourceID varchar(80),
timestamp timestamp,
rel_id varchar(50),
klockslag varchar(10),
grupp varchar(20),
format varchar(20),
intressent_id char(13),
mottagare_id char(13),
mottagare varchar(80),
hangar_id integer,
plats varchar(150),
slutdatum timestamp,
webbtvlive smallint
);



CREATE TABLE organ (
id integer,
kod varchar(50),
namn varchar(100),
typ varchar(50),
status varchar(12),
sortering integer,
namn_en varchar(100),
doman varchar(50),
beskrivning varchar(1000)
);



CREATE TABLE roll (
pk integer,
kod varchar(50),
namn varchar(100),
sort int
);



CREATE TABLE riksmote (
pk integer,
riksmote varchar(20),
id varchar(3),
start timestamp,
slut timestamp,
mandatperiod varchar(20)
);