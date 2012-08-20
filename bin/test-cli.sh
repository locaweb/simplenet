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

echo "Creating Datacenter"
./simplenet-cli datacenter create ita | sed 's/,\|"//g' | ccze -A
dcid=$(./simplenet-cli datacenter info ita | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Zone"
./simplenet-cli zone create ita01 --datacenter_id $dcid | sed 's/,\|"//g' | ccze -A
./simplenet-cli zone create ita02 --datacenter_id $dcid | sed 's/,\|"//g' | ccze -A
nid=$(./simplenet-cli zone info ita01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
nid2=$(./simplenet-cli zone info ita02 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Vlan"
./simplenet-cli vlan create vlan01 --zone_id $nid | ccze -A
./simplenet-cli vlan create vlan02 --zone_id $nid2 | ccze -A
vid=$(./simplenet-cli vlan info vlan01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
vid2=$(./simplenet-cli vlan info vlan02 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Subnet"
./simplenet-cli subnet create 192.168.0.0/24 --vlan_id $vid | ccze -A
sid=$(./simplenet-cli subnet info 192.168.0.0/24 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Ip"
./simplenet-cli ip create 192.168.0.1 --subnet_id $sid | ccze -A
iid=$(./simplenet-cli ip info 192.168.0.1 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo "Next ip creation must fail"
./simplenet-cli ip create 192.168.1.1 --subnet_id $sid | ccze -A
echo

echo "Creating Device"
./simplenet-cli device create firewall01 --zone_id $nid | ccze -A
./simplenet-cli device create firewall02 --zone_id $nid2 | ccze -A
dic=$(./simplenet-cli device info firewall01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
dic2=$(./simplenet-cli device info firewall02 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating policy to zone"
pnid=$(./simplenet-cli policy create zone $nid --src 192.168.0.1 --proto tcp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info zone $pnid | ccze -A
echo

echo "Creating policy to vlan"
pvid=$(./simplenet-cli policy create vlan $vid --dst_port 53 --proto udp --table INPUT --policy ACCEPT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info vlan $pvid | ccze -A
echo

echo "Creating policy to subnet"
psid=$(./simplenet-cli policy create subnet $sid --dst 192.168.0.2 --proto tcp --table OUTPUT --policy DROP | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info subnet $psid | ccze -A
echo

echo "Creating policy to ip"
piid=$(./simplenet-cli policy create ip $iid --src 192.168.0.2 --proto udp --table FORWARD --policy REJECT | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
./simplenet-cli policy info ip $piid | ccze -A
echo

echo "Attaching Vlan to Device"
./simplenet-cli device attach $dic2 --vlan_id $vid | ccze -A
echo "Next attach creation must fail"
./simplenet-cli device attach $dic --vlan_id $vid | ccze -A
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

echo "Delete vlan Zone"
./simplenet-cli policy delete zone $pnid
echo

echo "Delete vlan policy"
./simplenet-cli policy delete vlan $pvid
echo

echo "Delete subnet policy"
./simplenet-cli policy delete subnet $psid
echo

echo "Delete ip policy"
./simplenet-cli policy delete ip $piid
echo

echo "Detaching Device"
./simplenet-cli device detach $dic --vlan_id $vid
echo

echo "Deleting Ip"
./simplenet-cli ip delete $iid
echo

echo "Deleting Subnet"
./simplenet-cli subnet delete $sid
echo

echo "Deleting Device"
./simplenet-cli device delete $dic
./simplenet-cli device delete $dic2
echo

echo "Deleting Vlan"
./simplenet-cli vlan delete $vid
./simplenet-cli vlan delete $vid2
echo

echo "Deleting Zone"
./simplenet-cli zone delete $nid
./simplenet-cli zone delete $nid2
echo

echo "Deleting Datacenter"
./simplenet-cli datacenter delete $dcid
echo