# Imports
from setuptools import setup

setup(
	name="goon",
	packages=["goon"],
	include_package_data=True,
	install_requires=["flask",
					  "requests",
					  "sqlalchemy",
					  "flask_sqlalchemy",
					  "psycopg2",],
)
