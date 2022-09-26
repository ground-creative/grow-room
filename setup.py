#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

PROJECT_DIR = os.path.dirname( os.path.realpath( __file__) )

def _load_readme( ):
	readme_path = os.path.join( PROJECT_DIR, 'README.md' )
	with codecs.open( readme_path, 'r', 'utf-8' ) as f:
		return f.read( )

setup(
	name='grow-room',
	version='1.0.0',
	description='Grow room app',
	long_description=_load_readme( ),
	author='Irony',
	author_email='carlo@ground-creative.com',
	install_requires=[ 
		'coloredlogs', 
		'logging', 
		'paho-mqtt', 
		'tuyalinksdk' 
	]
)