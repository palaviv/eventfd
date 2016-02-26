#!/usr/bin/env python
from setuptools import setup

setup(
    name='eventfd',
    version=0.1,
    py_modules=['eventfd'],
    license='Simplified BSD License',
    description='threading.Event like class that has a file descriptor and can be used in select/poll',
    long_description=open('README.txt').read(),
    author='Aviv Palivoda',
    author_email='palaviv@gmail.com',
    url='http://eventfd.readthedocs.org'
)
