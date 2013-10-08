## What is simplenet?
Simplenet is a framework for network automation. Using simplenet you can easily manage boxes from diferente verdors using an uniq api and cli. The idea behind simplenet is create an abstraction layer turning simple to administer and adpot of new products.

<img src="https://raw.github.com/locaweb/simplenet/master/simplenet.png">

## Config:
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

## Instalation:
### Packaging on Debian and Ubuntu

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

### Cli

	$ dpkg -i simplenet-cli_x.x.x-x_amd64.deb
	$ /usr/sbin/simplenet-cli 
	Usage: /usr/sbin/simplenet-cli COMMAND <options>

	Available commands:
	 anycast       Manage an anycast subnet
	 anycastip     Manage an ip contained in a anycast subnet
	 datacenter    Manage the datacenter entity
	 firewall      Manage a firewall device related to a zone
	 firewallrule  Manage firewall rules
	 ip            Manage an ip contained in a subnet
	 subnet        Manage a subnet related to a vlan
	 vlan          Manage a vlan related to a zone
	 zone          Manage a zone related to a datacenter

	Use '/usr/sbin/simplenet-cli <command> --help' for individual command help.

## Depends:

* baker      - https://pypi.python.org/pypi/Baker
* kombu      - https://pypi.python.org/pypi/kombu
* bootle     - https://pypi.python.org/pypi/bottle
* ipaddr     - https://pypi.python.org/pypi/ipaddr
* requests   - https://github.com/kennethreitz/requests
* sqlalchemy - https://bitbucket.org/zzzeek/sqlalchemy
