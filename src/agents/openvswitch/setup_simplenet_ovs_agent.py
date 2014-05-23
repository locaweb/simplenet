#!/usr/bin/python2.6

from distutils.core import setup

setup(name='simplenet-ovs-agent',
      version='0.2.0',
      description='Simplenet OpenVSwitch Agent',
      author='Luiz Ozaki',
      author_email='luiz.ozaki@locaweb.com.br',
      url='https://github.com/locaweb/simplenet',
      data_files=[('/etc/simplenet', ['agents.cfg']),
                  ('/etc/init.d', ['simplenet-ovs-agent']),
                  ('/usr/sbin', ['sn-ovs-agent'])]
     )
