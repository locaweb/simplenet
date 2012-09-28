#!/usr/bin/python

from setuptools import setup, find_packages
from glob import glob as ls

setup(
    name = 'simplenet-server',
    version = '0.0.3',
    description = 'Network automation framework',
    long_description = 'Network automation framework',
    author = 'Juliano Martinez',
    author_email = 'juliano.martinez@locaweb.com.br',
    maintainer = 'Juliano Martinez',
    maintainer_email = 'juliano.martinez@locaweb.com.br',
    url = 'https://git.locaweb.com.br/locastack/simplenet',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    licence = 'Apache',
    data_files=[('/usr/sbin', ['src/sbin/simplenet-server'])
                ('/etc/simplenet', ['src/conf/simplenet.cfg'])],
)
