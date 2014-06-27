#!/bin/bash

# Copyright 2012 Locaweb.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @author: Juliano Martinez (ncode), Locaweb.
set -o pipefail

function run_test(){
    START=`date +%s.%N`
    local cmd="$1"
    local to_find="$2"
    simplenet="../src/sbin/simplenet-cli"
    echo "::  Running ${simplenet/*\//} $cmd"
    echo -n "::: Status ->  "
    result=$($simplenet $cmd 2>&1)
    if !( echo "$result" | grep -qw "$to_find" ) ; then
        echo -e "\033[01;31m[ FAIL ]\033[00m"
        echo "Unable to $cmd"
        echo "Expected: $to_find"
        echo "Got $result"
    else
        if [ "$to_find" == '' ] ; then
            echo -e "\033[01;32m[ OK ]\033[00m"
        else
            echo -e "\033[01;32m[ OK ]\033[00m Result: $to_find"
        fi
    fi
    END=`date +%s.%N`
    TT=`echo $END-$START | bc -l`
    echo "DURATION: $TT"
}

function run_firewall_test(){
    local action="$1"
    local rule_type="$2"
    local cmd="$1 $2 $3"
    local simplenet="../src/sbin/simplenet-cli"
    echo "::  Running ${simplenet/*\//} $cmd"
    echo -n "::: Status ->  "
    local result=$($simplenet $cmd 2>&1)
    local rule_id=$(echo "$result" | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
    if [ $(echo "$rule_id" | wc -c) != 37 ]; then
        echo -e "\033[01;31m[ FAIL ]\033[00m"
        echo "Unable to $cmd"
        echo "Got $result"
    else
        echo -e "\033[01;32m[ OK ]\033[00m Result: ${rule_id}"
        run_test "firewallrule info $rule_type ${rule_id}" '"id": "'${rule_id}'"'
    fi
}

for i in `seq 1 5`;
do sw=$(( $RANDOM % 400 + 1 ))

for i in `seq 1 5`;
do
vlan=$(( $RANDOM % 400 + 1 ))
firewall=$(( $RANDOM % 400 + 1 ))
range=$(( $RANDOM % 253 + 1 ))
pod=$(( $RANDOM % 10 + 1 ))

if [ $1 == "ip" ] || [ $1 == "all" ] || ! [ $1 ]; then
    echo -e "\n::::: Starting Ip Tests "
    run_test "datacenter create datacenter01" '"name": "datacenter01"'
    run_test "pod create pod$pod --datacenter datacenter01" "\"name\": \"pod$pod\""
    run_test "vlan create vlan$vlan --pod pod$pod --number $vlan --type dedicated_vlan" "\"name\": \"vlan$vlan\""
    run_test "firewall create firewall$firewall --pod pod$pod" "\"name\": \"firewall$firewall\""
    run_test "subnet create 192.168.$range.0/24 --vlan vlan$vlan" "\"cidr\": \"192.168.$range.0/24\""
    run_test "ip create 192.168.$range.1 --subnet 192.168.$range.0/24" "\"ip\": \"192.168.$range.1\""
    run_firewall_test "firewallrule create" "subnet" "192.168.$range.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP"
    run_firewall_test "firewallrule create" "subnet" "192.168.$range.0/24 --dst 192.168.0.2 --proto tcp --table FORWARD --policy DROP"
    run_firewall_test "firewallrule create" "subnet" "192.168.$range.0/24 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP"
    run_firewall_test "firewallrule create" "ip" "192.168.$range.1 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP"
fi

if [ $1 == "interface" ] || [ $1 == "all" ] || ! [ $1 ]; then
    echo -e "\n::::: Starting Interface Tests "
    run_test "vlan create vlan$vlan --pod pod01 --type private_vlan --number $vlan" "\"name\": \"vlan$vlan\""
    fwmac=`(date; cat /proc/interrupts) | md5sum | sed -r 's/^(.{12}).*$/\1/; s/([0-9a-f]{2})/\1:/g; s/:$//;'`
    run_test "firewall create firewall$firewall --pod pod01 --mac $fwmac" "\"name\": \"firewall$firewall\""
    run_test "dhcp create dhcp$vlan" "\"name\": \"dhcp$vlan\""
    run_test "dhcp vlan_attach dhcp$vlan --vlan vlan$vlan" "\"name\": \"dhcp$vlan\""
    run_test "subnet create 192.168.$range.0/24 --vlan vlan$vlan" "\"cidr\": \"192.168.$range.0/24\""
    swmac=`(date; cat /proc/interrupts) | md5sum | sed -r 's/^(.{12}).*$/\1/; s/([0-9a-f]{2})/\1:/g; s/:$//;'`
    run_test "switch create sw$sw --model_type openvswitch --address tcp:127.0.0.1:8088 --mac $swmac" "\"name\": \"sw$sw\""
    for i in `seq 1 10`;
    do
        ip=$(( $RANDOM % 253 + 1 ))
        run_test "ip create 192.168.$range.$ip --subnet 192.168.$range.0/24" "\"ip\": \"192.168.$range.$ip\""
        mac=`(date; cat /proc/interrupts) | md5sum | sed -r 's/^(.{12}).*$/\1/; s/([0-9a-f]{2})/\1:/g; s/:$//;'`
        run_test "interface create $mac" "\"id\": \"$mac\""
        run_test "interface ip_attach $mac 192.168.$range.$ip" "\"id\": \"$mac\""
        a=$(( $RANDOM % 100 + 1 ))
        b=$(( $RANDOM % 100 + 1 ))
        c=$(( $RANDOM % 100 + 1 ))
        run_test "switch int_attach sw$sw --inter $mac --int_name vif$a.$b --ofport $c" "\"id\": \"$mac\""
    done
fi
done
done
