What is simplenet?
==================

Simplenet is a framework for network automation. Using simplenet you can easily manage boxes from diferent verdors using an unique api and cli. The idea behind simplenet is to create an abstraction layer simplifying management and adoption of new network products.

![simplenet infrastructure](https://raw.github.com/locaweb/simplenet/master/simplenet.png)


Configuration
-------------

### simplenet.cfg

	[server]
	port = 8081                                # port to bind the api
	debug = True                               # enable or disable the debug
	bind_addr = 0.0.0.0                        # address to bind
	timeout = 60                               # timeout per request
	user = simplestack                         # username to run the api
	database_type = mysql                      # or any db supported by sqlalchemy
	database_name = simplenet                  # db username or sqlite file path
	database_host = 127.0.0.1                  # db hostname
	database_user = simplenet_user             # db usermame
	database_pass = simplenet_pass             # db password

	[event]
	broker = amqp://guest:guest@localhost//    # amqp broker connection

	[redis]
	host = 127.0.0.1                           # redis hostname
	port = 6379                                # redis port

	[authentication]
	enabled = False                            # authentication plugin

### agents.cfg

	[firewall]
	lockfile = /var/run/firewall-agent.lock    # firewall agent lockfile
	broker = amqp://guest:guest@localhost//    # amqp broker connection
	iptables_file = /etc/iptables/rules        # iptables files
	logging = debug                            # log level


Instalation
-----------

### Debian / Ubuntu packaging

        $ git clone https://github.com/locaweb/simplenet.git
        $ cd simplenet
        $ dpkg-buildpackage -us -uc -rfakeroot
        $ ls ../simplenet*.deb
        $ simplenet-cli_x.x.x-x_amd64.deb
        $ simplenet-firewall-agent_x.x.x-x_amd64.deb
        $ simplenet-server_x.x.x-x_amd64.deb

### Firewall

	$ dpkg -i simplenet-firewall-agent_x.x.x-x_amd64.deb
	$ /etc/init.d/simplenet-firewall-agent start

### Server

	$ dpkg -i simplenet-server_x.x.x-x_amd64.deb
	$ /etc/init.d/simplenet-server start

### Command line interface

	$ dpkg -i simplenet-cli_x.x.x-x_amd64.deb
	$ /usr/sbin/simplenet-cli
	Usage: /usr/sbin/simplenet-cli COMMAND <options>

        Available commands:
                anycast       Manage an anycast subnet
                anycastip     Manage an ip contained in a anycast subnet
                datacenter    Manage the datacenter entity
                dhcp          Manage a dhcp server related to a vlan
                firewall      Manage a firewall device related to a zone
                firewallrule  Manage firewall rules
                interface
                ip            Manage an ip contained in a subnet
                pod           Manage a POD (zone) related to a datacenter
                router        Manage router entity
                subnet        Manage a subnet related to a vlan
                switch
                vlan          Manage a vlan related to a POD (zone)

	Use '/usr/sbin/simplenet-cli <command> --help' for individual command help.


Tests
-----

Simplenet implements integration tests via CLI.
In order to run the test suite on the development machine you need to have up and running:

* redis
* rabbitmq
* mysql
* simplenet server

and then just run `try.sh` file on `try` directory.


Dependencies
------------

* baker      - https://pypi.python.org/pypi/Baker
* kombu      - https://pypi.python.org/pypi/kombu
* bootle     - https://pypi.python.org/pypi/bottle
* ipaddr     - https://pypi.python.org/pypi/ipaddr
* requests   - https://github.com/kennethreitz/requests
* sqlalchemy - https://bitbucket.org/zzzeek/sqlalchemy

For specific versions on development please refer to `pip_requires` file.
