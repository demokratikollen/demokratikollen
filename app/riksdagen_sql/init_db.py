from subprocess import call

filelist = [
	'create_tables.sql',
	'psql_person.sql'
]

def main():
	for f in filelist:
		print('Running {}'.format(f))
		call(["psql", "-d riksdagen -U vagrant -q -f ", f])
	

if __name__ == '__main__':
	main()