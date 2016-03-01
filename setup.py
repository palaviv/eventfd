#!/usr/bin/env python
from setuptools import setup, Extension
import os

extensions = []

if os.name != "nt":
    extensions.append(Extension("eventfd._eventfd_c", sources=["eventfd/_eventfd.c"]))

setup(
    name='eventfd',
    version=open('VERSION.txt').read().strip(),
    packages=['eventfd'],
    license='Simplified BSD License',
    description='threading.Event like class that has a file descriptor and can be used in select/poll',
    long_description=open('README.txt').read(),
    author='Aviv Palivoda',
    author_email='palaviv@gmail.com',
    url='http://eventfd.readthedocs.org',
    ext_modules=extensions
)
