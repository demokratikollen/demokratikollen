import urllib.request
import urllib.parse	
import os.path
from subprocess import call

urllist = [
	'http://data.riksdagen.se/dataset/person/person.sql.zip',
	'http://data.riksdagen.se/dataset/votering/votering-201314.sql.zip'
]

def main():
	for url in urllist:

		urlparts = urllib.parse.urlparse(url)
		filename = os.path.split(urlparts.path)[1]
		print('Downloading {}'.format(filename))
		urllib.request.urlretrieve(url, filename)
		call(["unzip", filename])
		call(["rm", filename])
		sqlfilename = filename[0:-4]
		print('Postgresifying {}'.format(sqlfilename))
		call(["python","postgresify.py",sqlfilename])
		call(["rm", sqlfilename])
	

if __name__ == '__main__':
	main()