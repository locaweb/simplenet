#!/usr/bin/python

from setuptools import setup

setup(
    name = 'simplenet-firewall-agent',
    version = '0.1.5',
    description = 'Network automation framework agent',
    long_description = 'Network automation framework firewall agent',
    author = 'Juliano Martinez',
    author_email = 'juliano@martinez.io',
    maintainer = 'Luiz Viana',
    maintainer_email = 'luiz.viana@locaweb.com.br',
    url = 'https://git.locaweb.com.br/locastack/simplenet',
    licence = 'Apache',
    data_files=[('/usr/sbin', ['src/agents/sn-fw-agent']),
                ('/etc/simplenet', ['src/conf/agents.cfg'])],
)
