#!/usr/bin/python

from setuptools import setup

setup(
    name = 'simplenet-cli',
    version = '0.1.5',
    description = 'Network automation framework cli',
    long_description = 'Network automation framework command line interface',
    author = 'Juliano Martinez',
    author_email = 'juliano@martinez.io',
    maintainer = 'Luiz Viana',
    maintainer_email = 'luiz.viana@locaweb.com.br',
    url = 'https://git.locaweb.com.br/locastack/simplenet',
    licence = 'Apache',
    data_files=[('/usr/sbin', ['src/sbin/simplenet-cli']),
                ('/etc/simplenet', ['src/conf/simplenet-cli.cfg'])],
)
