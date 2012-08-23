#!/usr/bin/python

from re import *
import commands
import json

def execute(cmd):
    print cmd
    data = (commands.getstatusoutput('../bin/simplenet-cli ' + cmd)[1])
    try:
        return json.loads(data)
    except:
        print "Failed to run " + cmd
        return data

f = file("sample","r")
execute("datacenter create ita")
datacenter = execute("datacenter info ita")

execute("zone create ita01 --datacenter ita")
zone = execute("zone info ita01")

execute("vlan create vlan01 --zone ita01")
vlan = execute("vlan info vlan01")

raw = f.read()

ranges = findall("(-d|-s)\s+(.*) -j (?!DROP |ACCEPT )", raw)

ip_ranges = []
for ranges in ranges:
    if (ranges[1] not in ip_ranges):
        ip_ranges.append(ranges[1])

for ranges in ip_ranges:
    execute("subnet create %s --vlan vlan01" % ranges)

filter1 = raw
replacers = [["-m udp ",""],["-m tcp ",""],["-m multiport ",""],[" -s"," --src"],[" -p", " --proto"],[" -d", " --dst"],[" --dport"," --dst_port"],[" -j", " --policy"]]
for a,b in replacers:
    filter1 = filter1.replace(a,b)

filter2 = findall("--.* ACCEPT |DROP ", filter1)

for item in filter2:
    match = ["dst_ports","src_ports", "sports", "dports"]
    if any(x in item for x in match):
        output = findall("(--.*)(--dst_ports|--sports) (.*) (--.*) ", item)[0]
        for ports in output[2].split(','):
            execute("policy create vlan vlan01 %s %s %s %s --table FORWARD" % (output[0],output[1].replace("ports","port").replace("sport","src_port"), ports, output[3]))
    elif not ("policy" in item):
        execute("policy create vlan vlan01 --policy %s --table FORWARD" % item)
    else:
        execute("policy create vlan vlan01 %s --table FORWARD" % item)

