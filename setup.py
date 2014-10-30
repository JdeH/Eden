import os

from setuptools import setup

def read (*paths):
	with open (os.path.join (*paths), 'r') as aFile:
		return aFile.read()

setup (
	name = 'Eden',
	version = '2.1.1',
	description = 'Eden - Event Driven Evaluation Nodes',
	long_description = (
		read ('README.md') + '\n\n' +
		read ('qQuickLicence.txt')
	),
	keywords = ['eden', 'kivy', 'winforms', 'observer', 'functional'],
	url = 'http://github.com/JdeH/eden/',
	license = 'qQuickLicence',
	author = 'Jacques de Hooge',
	author_email = 'jacques.de.hooge@qquick.org',
	py_modules = ['eden'],
	include_package_data = True,
	install_requires = ['Kivy'],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: Other/Proprietary License',
	'Topic :: Software Development :: Libraries :: Python Modules',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
	],
)
