#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

setup(
	name='grow-room',
	version='1.0',
	description='Grow room app',
	author='Irony',
	author_email='carlo@ground-creative.com',
	#packages=['grow-room'],  #same as name
	install_requires=[ 
		'coloredlogs', 
		'logging', 
		'paho-mqtt', 
		'tuyalinksdk' 
	]#, #external packages as dependencies
	#python_requires='>=3.6'
)