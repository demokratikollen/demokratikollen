import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
	name = "Demokratikollen",
	version = "0.1",
	packages = find_packages(),
	install_requires = ['sqlalchemy','psycopg2'],
)
