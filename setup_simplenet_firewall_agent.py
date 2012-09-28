#!/usr/bin/python

from setuptools import setup

setup(
    name = 'simplenet-firewall-agent',
    version = '0.0.3',
    description = 'Network automation framework cli',
    long_description = 'Network automation framework cli',
    author = 'Juliano Martinez',
    author_email = 'juliano.martinez@locaweb.com.br',
    maintainer = 'Juliano Martinez',
    maintainer_email = 'juliano.martinez@locaweb.com.br',
    url = 'https://git.locaweb.com.br/locastack/simplenet',
    licence = 'Apache',
    data_files=[('/usr/sbin', ['src/agent/sn-fw-agent']),
                ('/etc/simplenet', ['src/conf/agent.cfg'])],
)
