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
}

function run_policy_test(){
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
        run_test "policy info $rule_type ${rule_id}" '"id": "'${rule_id}'"'
        run_test "policy delete $rule_type ${rule_id}" '"message": "Successful deletetion"'
    fi
}

echo "::::: Starting Datacenter Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "datacenter create datacenter01" '"message": "Datacenter:datacenter01 already exists Forbidden"'
run_test "datacenter info datacenter01" '"name": "datacenter01"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Zone Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_policy_test "policy create" "zone" "zone01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT"
run_test "zone info zone01" '"name": "zone01"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Device Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "device create firewall01 --zone zone01" '"name": "firewall01"'
run_test "device create firewall01 --zone zone01" '"message": "Device:firewall01 already exists Forbidden"'
run_test "device info firewall01" '"name": "firewall01"'
run_test "device delete firewall01" '"message": "Successful deletetion"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Vlan Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "vlan create vlan01 --zone zone01" '"name": "vlan01"'
run_test "vlan create vlan01 --zone zone01" '"message": "Vlan:vlan01 already exists Forbidden"'
run_policy_test "policy create" "vlan" "vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT"
run_policy_test "policy create" "vlan" "vlan01 --dst_port 80 --proto tcp --table INPUT --policy ACCEPT"
run_policy_test "policy create" "vlan" "vlan01 --dst_port 443 --proto tcp --table INPUT --policy ACCEPT"
run_test "vlan info vlan01" '"name": "vlan01"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Subnet Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02" '"name": "vlan02"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"message": "Subnet:192.168.0.0/24 already exists Forbidden"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "subnet info 192.168.0.0/24" '"cidr": "192.168.0.0/24"'
run_test "subnet info 192.168.0.1/24" '"cidr": "192.168.0.1/24"'
run_test "subnet delete 192.168.0.0/24" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.1/24" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "vlan delete vlan02" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "zone delete zone02" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Anycast Tests "
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycast create 192.168.168.0/24" '"message": "Anycast:192.168.168.0/24 already exists Forbidden"'
run_test "anycast info 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycast delete 192.168.168.0/24" '"message": "Successful deletetion"'

echo -e "\n::::: Starting Ip Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02" '"name": "vlan02"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "ip create 192.168.0.1 --subnet 192.168.0.0/24" '"ip": "192.168.0.1"'
run_test "ip create 192.168.1.1 --subnet 192.168.0.1/24" '"message": "Ip:192.168.1.1 address must be contained in 192.168.0.1/24 Forbidden"'
run_policy_test "policy create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP"
run_policy_test "policy create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table FORWARD --policy DROP"
run_policy_test "policy create" "subnet" "192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP"
run_test "ip info 192.168.0.1" '"ip": "192.168.0.1"'
run_test "ip delete 192.168.0.1" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.0/24" '"message": "Successful deletetion"'
run_test "subnet delete 192.168.0.1/24" '"message": "Successful deletetion"'
run_test "vlan delete vlan01" '"message": "Successful deletetion"'
run_test "vlan delete vlan02" '"message": "Successful deletetion"'
run_test "zone delete zone01" '"message": "Successful deletetion"'
run_test "zone delete zone02" '"message": "Successful deletetion"'
run_test "datacenter delete datacenter01" '"message": "Successful deletetion"'

echo -e "\n::::: Starting IpAnycast Tests "
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycastip create 192.168.168.3 --anycast 192.168.168.0/24" '"ip": "192.168.168.3"'
run_test "anycastip create 192.168.0.3 --anycast 192.168.168.0/24" '"message": "Ip:192.168.0.3 address must be contained in 192.168.168.0/24 Forbidden"'
run_policy_test "policy create" "anycast" "192.168.168.0/24 --dst 192.168.168.3 --proto tcp --table OUTPUT --policy DROP"
exit
run_test "anycastip info 192.168.168.3" '"ip": "192.168.168.3"'
run_test "anycastip delete 192.168.168.3" '"message": "Successful deletetion"'
run_test "anycast delete 192.168.168.0/24" '"message": "Successful deletetion"'

exit

echo "Creating and list policy anycast subnet"
paid=$(./simplenet-cli policy create anycast 192.168.168.0/24 --dst 192.168.168.3 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

./simplenet-cli device anycast_attach fireany01 --anycast 192.168.168.0/24 | ccze -A
./simplenet-cli device anycast_attach fireany02 --anycast 192.168.168.0/24 | ccze -A

echo "Creating and list policy ip"
piid=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
piid2=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.3 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
piid3=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.4 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info ip $piid | ccze -A
./simplenet-cli policy info ip all | ccze -A
echo

echo "Creating and list policy anycast ip"
paid2=$(./simplenet-cli policy create anycastip 192.168.168.3 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Attaching Vlan to Device"
./simplenet-cli device vlan_attach firewall01 --vlan vlan01 | ccze -A
echo "Next attach creation must fail"
./simplenet-cli device vlan_attach firewall02 --vlan vlan01 | ccze -A
if [ $? -ne 1 ]; then
    echo "Return must FAIL but it has exited OK"
    exit 1
fi
echo

echo "Reverse policy"
echo "Creating and list policy ip"
revpiid=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy anycast ip"
revpaid2=$(./simplenet-cli policy create anycastip 192.168.168.3 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy anycast subnet"
revpaid=$(./simplenet-cli policy create anycast 192.168.168.0/24 --dst 192.168.168.3 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy subnet"
revpsid=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy vlan"
revpvid=$(./simplenet-cli policy create vlan vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy zone"
revpnid=$(./simplenet-cli policy create zone ita01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Detaching Device"
./simplenet-cli device vlan_detach firewall01 --vlan vlan01
echo
