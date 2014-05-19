========
Base API
========

/v1/prober
==========

Method GET
----------

:status: * 200 Ok
         * xxx Error

Do a SQL query for DB status

Example::

    $ curl http://localhost:8081/v1/prober


/v1/<resource>
===================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieves all entries from resource

:resource:
           * datacenters
           * zones
           * vlans
           * subnets
           * anycasts
           * ips
           * anycastips
           * firewalls
           * dhcps
           * switches
           * interfaces

Example::

    $ curl http://localhost:8081/v1/switches | python -m json.tool
    [
        {
            "address": "x.x.x.x:yyyy",
            "id": "b9143a51-02de-442e-a950-ef56cfdf540f",
            "mac": "FF:FF:FF:FF:FF:FF",
            "model_type": "openvswitch",
            "name": "vswitch01"
        },
        {
            "address": "y.y.y.y:xxxx",
            "id": "c9fa2ed2-f356-4e2c-99c7-9c6d44833df9",
            "mac": "00:00:00:00:00:00",
            "model_type": "openvswitch",
            "name": "vswitch02"
        }
    ]


/v1/<resource>/<resource_id>
=================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieves resource by id

Example::

    $ curl http://localhost:8081/v1/switches/b9143a51-02de-442e-a950-ef56cfdf540f | python -m json.tool
    {
        "address": "x.x.x.x:yyyy",
        "id": "b9143a51-02de-442e-a950-ef56cfdf540f",
        "mac": "FF:FF:FF:FF:FF:FF",
        "model_type": "openvswitch",
        "name": "vswitch01"
    }


/v1/<resource>/by-<resource_type>/<resource_value>
==================================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieves resource information by resource field

Example::

    $ curl http://localhost:8081/v1/switches/by-name/vswitch01 | python -m json.tool
    {
        "address": "x.x.x.x:yyyy",
        "id": "b9143a51-02de-442e-a950-ef56cfdf540f",
        "mac": "FF:FF:FF:FF:FF:FF",
        "model_type": "openvswitch",
        "name": "vswitch01"
    }



/v1/<resource>/list-by-<relationship_type>/<relationship_value>
===============================================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieves resource information by relationship
relationship_value needs to be a valid id

Example::

    List all DHCPs that belongs to the vlan with id d9dff147-28d4-42c4-b620-032681eabeec
    $ curl http://localhost:8081/v1/dhcps/list-by-vlan/d9dff147-28d4-42c4-b620-032681eabeec
    [
        {
            "dhcp_id": "5e4a126a-b1a2-4af8-89b6-8e88443067ae",
            "name": "dhcp01",
            "vlan": "vlan01",
            "vlan_id": "d9dff147-28d4-42c4-b620-032681eabeec"
        },
        {
            "dhcp_id": "e1693fe2-f1b6-4e56-8cc7-d69c54bcb5d4",
            "name": "dhcp02",
            "vlan": "vlan01",
            "vlan_id": "d9dff147-28d4-42c4-b620-032681eabeec"
        }
    ]


/v1/<resource>/<resource_id>
==================================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Delete a resource by id

Example::

    $ curl http://localhost:8081/v1/firewalls/b571d92f-284d-41ff-9378-c5d4fa4cdee4
    HTTP 200


/v1/datacenters
===============

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new datacenter

Example::

    $ curl http://localhost:8081/v1/datacenters -d '{"name": "datacenter02"}' -X POST | python -m json.tool
    {
        "id": "a0c72c62-c312-4273-92db-363f52c1682f",
        "name": "datacenter02"
    }


/v1/zones
=====================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new zone in datacenter

Example::

    $ curl http://localhost:8081/v1/zones -d '{"name": "zone000", "datacenter_id": "a0c72c62-c312-4273-92db-363f52c1682f"}' -X POST | python -m json.tool
    {
        "datacenter": "datacenter02",
        "datacenter_id": "a0c72c62-c312-4273-92db-363f52c1682f",
        "id": "cd819175-e810-4cda-ba77-c7a300ff9648",
        "name": "zone000"
    }


/v1/dhcps
=========

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new DHCP

Example::

    $ curl http://localhost:8081/v1/dhcps -d '{"name": "dhcp03", "vlan_id": "d9dff147-28d4-42c4-b620-032681eabeec"}' -X POST | python -m json.tool
    {
        "id": "3542f6d4-c33b-41a3-a543-030c0d441d1c",
        "name": "dhcp03"
    }


/v1/dhcps/<dhcp_id>/vlans
=========================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Attach vlan to DHCP device

Example::

    $ curl http://localhost:8081/v1/dhcps/3542f6d4-c33b-41a3-a543-030c0d441d1c/vlans -d '{"vlan_id": "d9dff147-28d4-42c4-b620-032681eabeec"}' -X POST | python -m json.tool
    {
        "id": "3542f6d4-c33b-41a3-a543-030c0d441d1c",
        "name": "dhcp03"
    }


/v1/dhcps/<dhcp_id>/vlans/<vlan_id>
===================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Detach vlan from DHCP device

Example::

    $ curl http://localhost:8081/v1/dhcps/3542f6d4-c33b-41a3-a543-030c0d441d1c/vlans/d9dff147-28d4-42c4-b620-032681eabeec -X DELETE
    HTTP 200


/v1/firewalls
=============

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new firewall

Example::

    $ curl http://localhost:8081/v1/firewalls -d '{"name": "firewall00", "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648", "mac": "11:11:11:11:11:11"}' -X POST
    {
        "address": null,
        "id": "036749a9-0da1-431f-8d48-24bd64a04429",
        "mac": "11:11:11:11:11:11",
        "name": "firewall00",
        "status": true,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }


/v1/firewall/enable
===================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Set firewall device to enabled

Example::

    $ curl http://localhost:8081/v1/firewall/enable -X POST -d '{"id": "036749a9-0da1-431f-8d48-24bd64a04429"}'
    {
        "address": null,
        "id": "036749a9-0da1-431f-8d48-24bd64a04429",
        "mac": "11:11:11:11:11:11",
        "name": "firewall00",
        "status": true,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }


/v1/firewall/disable
====================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Set firewall device to disable
Firewall stop receiving rules updates when its disabled

Example::

    $ curl http://localhost:8081/v1/firewall/enable -X POST -d '{"id": "036749a9-0da1-431f-8d48-24bd64a04429"}'
    {
        "address": null,
        "id": "036749a9-0da1-431f-8d48-24bd64a04429",
        "mac": "11:11:11:11:11:11",
        "name": "firewall00",
        "status": false,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }


/v1/firewall/sync
=================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Reload firewall rules

Example::

    $ curl http://localhost:8081/v1/firewall/sync -X POST -d '{"name": "firewall00"}'
    {
        "address": null,
        "id": "036749a9-0da1-431f-8d48-24bd64a04429",
        "mac": "11:11:11:11:11:11",
        "name": "firewall00",
        "status": true,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }

/v1/vlans
=========================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

:type:
    * private_vlan
    * dedicated_vlan

Create a new vlan at zone

Example::

    $ curl http://localhost:8081/v1/vlans -d '{"name": "vlan000", "type": "private_vlan", "vlan_num": 1, "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"}' -X POST
    {
        "id": "6000cc53-f9ba-4340-bdf0-d6ed615fa05a",
        "name": "vlan000",
        "type": "private_vlan",
        "vlan_num": 1,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }


/v1/anycasts
============

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new anycast network subnet

Example::

    $ curl http://localhost:8081/v1/anycasts -d '{"cidr": "192.168.0.0/24"}' -X POST
    {
        "cidr": "192.168.0.0/24",
        "id": "55b0b07e-cbbc-4477-a7d4-8dd7f07d380c"
    }


/v1/firewalls/<firewall_id>/anycasts
====================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Attach a anycast subnet to the firewall

Example::

    $ curl http://localhost:8081/v1/firewalls/036749a9-0da1-431f-8d48-24bd64a04429/anycasts -d '{"anycast_id": "55b0b07e-cbbc-4477-a7d4-8dd7f07d380c"}' -X POST
    {
        "address": null,
        "id": "036749a9-0da1-431f-8d48-24bd64a04429",
        "mac": "11:11:11:11:11:11",
        "name": "firewall00",
        "status": true,
        "zone": "zone000",
        "zone_id": "cd819175-e810-4cda-ba77-c7a300ff9648"
    }


/v1/firewalls/<firewall_id>/anycasts/<anycast_id>
=================================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Detach a anycast subnet from the firewall

Example::

    $ curl http://localhost:8081/v1/firewalls/036749a9-0da1-431f-8d48-24bd64a04429/anycasts/55b0b07e-cbbc-4477-a7d4-8dd7f07d380c -X DELETE
    HTTP 200


/v1/subnets
===========================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new subnet in vlan

Example::

    $ curl http://localhost:8081/v1/subnets -d '{"cidr": "10.0.0.0/24", "vlan_id": "6000cc53-f9ba-4340-bdf0-d6ed615fa05a"}' -X POST
    {
        "cidr": "10.0.0.0/24",
        "gateway": "10.0.0.1",
        "id": "2368f084-426c-4a39-a07e-f65236e6bb91",
        "ips": [],
        "network": "10.0.0.0/255.255.255.0",
        "vlan": "vlan000",
        "vlan_id": "6000cc53-f9ba-4340-bdf0-d6ed615fa05a"
    }

/v1/anycastips
====================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new ip in anycast subnet

Example::

    $ curl http://localhost:8081/v1/anycastips -d '{"ip": "192.168.0.100", "anycast_id": "55b0b07e-cbbc-4477-a7d4-8dd7f07d380c"}' -X POST
    {
        "anycast": "192.168.0.0/24",
        "anycast_id": "55b0b07e-cbbc-4477-a7d4-8dd7f07d380c",
        "id": "0b3749a3-1942-468f-bf70-13ab2b7eeff9",
        "ip": "192.168.0.100"
    }

/v1/ips
===========================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new ip in subnet

Example::

    $ curl http://localhost:8081/v1/ips -d '{"ip": "10.0.0.100", "subnet_id": "2368f084-426c-4a39-a07e-f65236e6bb91"}' -X POST | python -m json.tool
    {
        "hostname": null,
        "id": "6ed4b2ec-133f-4be6-9620-d90041475259",
        "interface_id": null,
        "ip": "10.0.0.100",
        "subnet": "10.0.0.0/24",
        "subnet_id": "2368f084-426c-4a39-a07e-f65236e6bb91"
    }


/v1/interfaces
==============

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new interface

Example::

    $ curl http://localhost:8081/v1/interfaces -d '{"mac": "55:55:55:55:55:55", "hostname": "host00"}' -X POST | python -m json.tool
    {
        "hostname": "host00",
        "id": "55:55:55:55:55:55",
        "ips": [],
        "name": null,
        "switch_id": null
    }


/v1/interfaces/<interface_id>/ips
=================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Attach IP to interface

Example::

    $ curl http://localhost:8081/v1/interfaces/55:55:55:55:55:55/ips -d '{"ip": "10.0.0.100"}' -X POST | python -m json.tool
    {
        "hostname": "host00",
        "id": "55:55:55:55:55:55",
        "ips": [
            "10.0.0.100"
        ],
        "name": null,
        "switch_id": null
    }


/v1/interfaces/<interface_id>/ips/<ip_id>
=========================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Detach ip from interface

Example::

    $ curl http://localhost:8081/v1/interfaces/55:55:55:55:55:55/ips/6ed4b2ec-133f-4be6-9620-d90041475259 -X DELETE
    {
        "hostname": "host00",
        "id": "55:55:55:55:55:55",
        "ips": [],
        "name": null,
        "switch_id": null
    }


==========
Policy API
==========

/v1/<network_appliance>/policy/<owner_type>/<id>
============================================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieve policy information

Example::

    $ curl http://127.0.0.1:8081/v1/firewall/policy/subnet/d47b3b0e-5579-4884-9af9-aac7b89c7c62 |  python -m json.tool
    {
        "dst": "10.0.0.100",
        "dst_port": "None",
        "id": "d47b3b0e-5579-4884-9af9-aac7b89c7c62",
        "owner": "10.0.0.0/24",
        "owner_id": "2368f084-426c-4a39-a07e-f65236e6bb91",
        "policy": "DROP",
        "proto": "tcp",
        "src": "None",
        "src_port": "None",
        "table": "INPUT"
    }


/v1/<network_appliance>/policy/<owner_type>/<owner_id>
======================================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new policy

Example::

    $ curl http://127.0.0.1:8081/v1/firewall/policy/subnet/2368f084-426c-4a39-a07e-f65236e6bb91 -d '{"src": "None", "src_port": "None", "dst_port": "None", "proto": "tcp", "policy": "DROP", "table": "INPUT", "dst": "10.0.0.100"}' -X POST | python -m json.tool
    {
        "dst": "10.0.0.100",
        "dst_port": "None",
        "id": "d47b3b0e-5579-4884-9af9-aac7b89c7c62",
        "owner": "10.0.0.0/24",
        "owner_id": "2368f084-426c-4a39-a07e-f65236e6bb91",
        "policy": "DROP",
        "proto": "tcp",
        "src": "None",
        "src_port": "None",
        "table": "INPUT"
    }


/v1/<network_appliance>/policy/<owner_type>/<id>
======================================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Deletes a policy

Example::

    $ curl http://127.0.0.1:8081/v1/firewall/policy/subnet/d47b3b0e-5579-4884-9af9-aac7b89c7c62 -X DELETE
    HTTP 200


/v1/<network_appliance>/policy/by-type/<owner_type>
========================================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieve all policy by type specified <owner_type>

Example::

    $ curl http://127.0.0.1:8081/v1/firewall/policy/by-type/subnet | python -m json.tool
    [
        {
            "dst": "10.0.0.100",
            "dst_port": "None",
            "id": "eb1b1c86-5c17-45e1-9a09-2e8214caf338",
            "owner": "10.0.0.0/24",
            "owner_id": "2368f084-426c-4a39-a07e-f65236e6bb91",
            "policy": "DROP",
            "proto": "tcp",
            "src": "None",
            "src_port": "None",
            "table": "INPUT"
        }
    ]


/v1/<network_appliance>/policy/by-owner/<owner_type>/<id>
======================================================

Method GET
----------

:status: * 200 Ok
         * xxx Error

Retrieve all policy from a given owner

Example::

    $ curl http://127.0.0.1:8081/v1/firewall/policy/by-owner/subnet/2368f084-426c-4a39-a07e-f65236e6bb91 | python -m json.tool
    [
        {
            "dst": "10.0.0.100",
            "dst_port": "None",
            "id": "eb1b1c86-5c17-45e1-9a09-2e8214caf338",
            "owner": "10.0.0.0/24",
            "owner_id": "2368f084-426c-4a39-a07e-f65236e6bb91",
            "policy": "DROP",
            "proto": "tcp",
            "src": "None",
            "src_port": "None",
            "table": "INPUT"
        }
    ]


==========
Switch API
==========

/v1/switches
===========

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Create a new switch

Example::

    $ curl http://127.0.0.1:8081/v1/switches -d '{"model_type": "openvswitch", "mac": "88:88:88:88:88:88", "name": "vswitch00", "address": "10.0.0.1:8888"}' -X POST | python -m json.tool
    {
        "address": "10.0.0.1:8888",
        "id": "cbb9163c-cc3d-4584-bcb4-8489b5f4db7e",
        "mac": "88:88:88:88:88:88",
        "model_type": "openvswitch",
        "name": "vswitch00"
    }


/v1/switches/<switch_id>/interfaces
==================================

Method POST
-----------

:status: * 200 Ok
         * xxx Error

Attach Interface to switch

Example::

    $ curl http://127.0.0.1:8081/v1/switches/cbb9163c-cc3d-4584-bcb4-8489b5f4db7e/interfaces -d '{"ofport": "5", "int_name": "vif1.0", "interface_id": "55:55:55:55:55:55"}' -X POST
    {
        "action": "plug",
        "firewalls": [],
        "hostname": "host00",
        "id": "55:55:55:55:55:55",
        "ips": [],
        "name": "vif1.0",
        "ofport": "5",
        "status": null,
        "switch_id": {
            "address": "10.0.0.1:8888",
            "id": "cbb9163c-cc3d-4584-bcb4-8489b5f4db7e",
            "mac": "88:88:88:88:88:88",
            "model_type": "openvswitch",
            "name": "vswitch00"
        }
    }


/v1/switches/<switch_id>/interfaces/<interface_id>
=================================================

Method DELETE
-------------

:status: * 200 Ok
         * xxx Error

Detach interface from switch

Example::

    $ curl http://127.0.0.1:8081/v1/switches/cbb9163c-cc3d-4584-bcb4-8489b5f4db7e/interfaces/55:55:55:55:55:55 -X DELETE
    {
        "action": "unplug",
        "hostname": "host00",
        "id": "55:55:55:55:55:55",
        "ips": [],
        "name": "vif1.0",
        "status": null,
        "switch_id": {
            "address": "10.0.0.1:8888",
            "id": "cbb9163c-cc3d-4584-bcb4-8489b5f4db7e",
            "mac": "88:88:88:88:88:88",
            "model_type": "openvswitch",
            "name": "vswitch00"
        }
    }
