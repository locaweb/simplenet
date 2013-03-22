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
        if [ "$to_find" != '' ] ; then
            echo -e "\033[01;32m[ OK ]\033[00m Result: $to_find"
        else
            echo -e "\033[01;32m[ OK ]\033[00m Result: $to_find"
        fi
    fi
}

echo "::::: Starting Datacenter Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "datacenter create datacenter01" '"message": "Datacenter:datacenter01 already exists Forbidden"'
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting Zone Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_test "zone delete zone01" ''
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting Device Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "device create firewall01 --zone zone01" '"name": "firewall01"'
run_test "device create firewall01 --zone zone01" '"name": "firewall01"'
run_test "device delete firewall01" ''
run_test "zone create zone01 --datacenter datacenter01" '"message": "Zone:zone01 already exists Forbidden"'
run_test "zone delete zone01" ''
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting Vlan Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "vlan create vlan01 --zone zone01" '"name": "vlan01"'
run_test "vlan create vlan01 --zone zone01" '"message": "Vlan:vlan01 already exists Forbidden"'
run_test "vlan delete vlan01" ''
run_test "zone delete zone01" ''
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting Subnet Tests "
run_test "datacenter create datacenter01" '"name": "datacenter01"'
run_test "zone create zone01 --datacenter datacenter01" '"name": "zone01"'
run_test "zone create zone02 --datacenter datacenter01" '"name": "zone02"'
run_test "vlan create vlan01 --zone zone01" '"name": "vlan01"'
run_test "vlan create vlan02 --zone zone02" '"name": "vlan02"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"cidr": "192.168.0.0/24"'
run_test "subnet create 192.168.0.0/24 --vlan vlan01" '"message": "Subnet:192.168.0.0/24 already exists Forbidden"'
run_test "subnet create 192.168.0.1/24 --vlan vlan02" '"cidr": "192.168.0.1/24"'
run_test "subnet delete 192.168.0.0/24" ''
run_test "subnet delete 192.168.0.1/24" ''
run_test "vlan delete vlan01" ''
run_test "vlan delete vlan02" ''
run_test "zone delete zone01" ''
run_test "zone delete zone02" ''
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting Anycast Tests "
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "anycast delete 192.168.168.0/24" ''

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
run_test "ip delete 192.168.0.1" ''
run_test "ip delete 192.168.1.1" ''
run_test "subnet delete 192.168.0.0/24" ''
run_test "subnet delete 192.168.0.1/24" ''
run_test "vlan delete vlan01" ''
run_test "vlan delete vlan02" ''
run_test "zone delete zone01" ''
run_test "zone delete zone02" ''
run_test "datacenter delete datacenter01" ''

echo -e "\n::::: Starting IpAnycast Tests "
run_test "anycast create 192.168.168.0/24" '"cidr": "192.168.168.0/24"'
run_test "ipanycast create 192.168.168.3 --anycast 192.168.168.0/24" '"ip": "192.168.168.1"'
run_test "ipanycast create 192.168.0.3 --anycast 192.168.168.0/24" '"message": "Ip:192.168.0.3 address must be contained in 192.168.168.0/24 Forbidden"'
run_test "ipanycast delete 192.168.168.3" ''
run_test "anycast delete 192.168.168.0/24" ''

exit

echo "Creating Device"
./simplenet-cli device create firewall01 --zone ita01 | ccze -A
./simplenet-cli device create firewall02 --zone ita02 | ccze -A
./simplenet-cli device create fireany01 --zone ita01 | ccze -A
./simplenet-cli device create fireany02 --zone ita01 | ccze -A
echo

echo "Creating and list policy zone"
pnid=$(./simplenet-cli policy create zone ita01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info zone $pnid | ccze -A
./simplenet-cli policy info zone all | ccze -A
echo

echo "Creating and list policy vlan"
pvid=$(./simplenet-cli policy create vlan vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
pvid2=$(./simplenet-cli policy create vlan vlan01 --dst_port 80 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
pvid3=$(./simplenet-cli policy create vlan vlan01 --dst_port 443 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info vlan $pvid | ccze -A
./simplenet-cli policy info vlan all | ccze -A
echo

echo "Creating and list policy subnet"
psid=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
psid2=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table FORWARD --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
psid3=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table INPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info subnet $psid | ccze -A
./simplenet-cli policy info subnet all | ccze -A
echo

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
paid2=$(./simplenet-cli policy create ipanycast 192.168.168.3 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

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
revpaid2=$(./simplenet-cli policy create ipanycast 192.168.168.3 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy anycast subnet"
revpaid=$(./simplenet-cli policy create anycast 192.168.168.0/24 --dst 192.168.168.3 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy subnet"
revpsid=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy vlan"
revpvid=$(./simplenet-cli policy create vlan vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy zone"
revpnid=$(./simplenet-cli policy create zone ita01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Listing Vlans atteched with device"
./simplenet-cli device vlan_list firewall01 | ccze -A
echo

echo "Listing Devices"
./simplenet-cli device list all | ccze -A
echo

echo "Listing Zones"
./simplenet-cli zone list all | ccze -A
echo

echo "Listing Vlans"
./simplenet-cli vlan list all | ccze -A
echo

echo "Listing Subnets"
./simplenet-cli subnet list all | ccze -A
echo

echo "Listing Anycast Subnets"
./simplenet-cli anycast list all | ccze -A
echo

echo "Listing Ip"
./simplenet-cli ip list all | ccze -A
echo

echo "Listing IpAnycast"
./simplenet-cli ipanycast list all | ccze -A
echo

exit

echo "Delete vlan Zone"
./simplenet-cli policy delete zone $pnid
./simplenet-cli policy delete zone $revpnid
echo

echo "Delete vlan policy"
./simplenet-cli policy delete vlan $revpvid
./simplenet-cli policy delete vlan $pvid
./simplenet-cli policy delete vlan $pvid2
./simplenet-cli policy delete vlan $pvid3
echo

echo "Delete anycast policy"
./simplenet-cli policy delete anycast $paid2
./simplenet-cli policy delete anycast $revpaid2

echo "Delete anycast policy"
./simplenet-cli policy delete anycast $paid
./simplenet-cli policy delete anycast $revpaid

echo "Delete subnet policy"
./simplenet-cli policy delete subnet $psid
./simplenet-cli policy delete subnet $revpsid
./simplenet-cli policy delete subnet $psid2
./simplenet-cli policy delete subnet $psid3
echo

echo "Delete ip policy"
./simplenet-cli policy delete ip $piid
./simplenet-cli policy delete ip $revpiid
./simplenet-cli policy delete ip $piid2
./simplenet-cli policy delete ip $piid3
echo

echo "Detaching Device"
./simplenet-cli device vlan_detach firewall01 --vlan vlan01
echo
