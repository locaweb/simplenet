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