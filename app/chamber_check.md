Angående fel i data rörande kammaruppdrag
=========================================

Vi hittar följande typer av fel:
 - Luckor då ingen sitter på en viss stol i kammaren
 - Perioder då två personer sitter på samma stol i kammaren
   - Ibland är felet 'trivialt': exempelvis Under en dag 2014-09-29 sitter både Eberstein, Susanne (S) och Billström, Tobias (M) på stol #1. Detta för att Tobias sitter _till och med_ och Susanne sitter _från och med_. Denna typ av fel uppträder ofta, men inte alltid (data är lite inkonsekvent) och det är inte så allvarligt.
   - I 41 fall är felet allvarligt i meningen att flera ledamöter är tilldelade samma stol under en längre tid.

Hur kollar vi?
--------------

Vi läser in

SELECT intressent_id,ordningsnummer,"from",tom,status,roll_kod FROM personuppdrag WHERE typ='kammaruppdrag' AND ordningsnummer!=0

Vi tittar på 
    role = "Ersättare" eller "Riksdagsledamot" (från 'roll_kod')
    status = "Ledig" eller "Tjänstgörande" (från 'status')
    chair = 'ordningsnummer'

På så vis ser vi vem som suttit när och på vilken stol i kammaren.

