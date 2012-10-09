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

echo "Creating Datacenter"
./simplenet-cli datacenter create ita | sed 's/,\|"//g' | ccze -A
echo

echo "Creating Zone"
./simplenet-cli zone create ita01 --datacenter ita | sed 's/,\|"//g' | ccze -A
./simplenet-cli zone create ita02 --datacenter ita | sed 's/,\|"//g' | ccze -A
echo

echo "Creating Vlan"
./simplenet-cli vlan create vlan01 --zone ita01 | ccze -A
./simplenet-cli vlan create vlan02 --zone ita02 | ccze -A
echo

echo "Creating Subnet"
./simplenet-cli subnet create 192.168.0.0/24 --vlan vlan01 | ccze -A
echo

echo "Creating Ip"
./simplenet-cli ip create 192.168.0.1 --subnet 192.168.0.0/24 | ccze -A
echo "Next ip creation must fail"
./simplenet-cli ip create 192.168.1.1 --subnet 192.168.0.0/24 | ccze -A
if [ $? -ne 1 ]; then
    echo "Return must FAIL but it has exited OK"
    exit 1
fi
echo

echo "Creating Device"
./simplenet-cli device create firewall01 --zone ita01 | ccze -A
./simplenet-cli device create firewall02 --zone ita02 | ccze -A
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

echo "Creating and list policy ip"
piid=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
piid2=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.3 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
piid3=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.4 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info ip $piid | ccze -A
./simplenet-cli policy info ip all | ccze -A
echo

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
piid=$(./simplenet-cli policy create ip 192.168.0.1 --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy subnet"
psid=$(./simplenet-cli policy create subnet 192.168.0.0/24 --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy vlan"
pvid=$(./simplenet-cli policy create vlan vlan01 --dst_port 53 --proto udp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

echo "Creating and list policy zone"
pnid=$(./simplenet-cli policy create zone ita01 --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')

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

echo "Listing Ip"
./simplenet-cli ip list all | ccze -A
echo

exit

echo "Delete vlan Zone"
./simplenet-cli policy delete zone $pnid
echo

echo "Delete vlan policy"
./simplenet-cli policy delete vlan $pvid
./simplenet-cli policy delete vlan $pvid2
./simplenet-cli policy delete vlan $pvid3
echo

echo "Delete subnet policy"
./simplenet-cli policy delete subnet $psid
./simplenet-cli policy delete subnet $psid2
./simplenet-cli policy delete subnet $psid3
echo

echo "Delete ip policy"
./simplenet-cli policy delete ip $piid
./simplenet-cli policy delete ip $piid2
./simplenet-cli policy delete ip $piid3
echo

echo "Detaching Device"
./simplenet-cli device vlan_detach firewall01 --vlan vlan01
echo

echo "Deleting Ip"
./simplenet-cli ip delete 192.168.0.1
echo

echo "Deleting Subnet"
./simplenet-cli subnet delete 192.168.0.0/24
echo

echo "Deleting Device"
./simplenet-cli device delete firewall01
./simplenet-cli device delete firewall02
echo

echo "Deleting Vlan"
./simplenet-cli vlan delete vlan01
./simplenet-cli vlan delete vlan02
echo

echo "Deleting Zone"
./simplenet-cli zone delete ita01
./simplenet-cli zone delete ita02
echo

echo "Deleting Datacenter"
./simplenet-cli datacenter delete ita
echo
