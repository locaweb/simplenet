#!/bin/bash

echo "Creating Neighborhood"
./simplenet-cli neighborhood create ita01 | sed 's/,\|"//g' | ccze -A
nid=$(./simplenet-cli neighborhood info ita01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Vlan"
./simplenet-cli vlan create vlan01 --neighborhood_id $nid | ccze -A
vid=$(./simplenet-cli vlan info vlan01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Subnet"
./simplenet-cli subnet create 192.168.0.0/24 --vlan_id $vid | ccze -A
sid=$(./simplenet-cli subnet info 192.168.0.0/24 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Ip"
./simplenet-cli ip create 192.168.0.1 --subnet_id $sid | ccze -A
iid=$(./simplenet-cli ip info 192.168.0.1 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Creating Device"
./simplenet-cli device create firewall01 --neighborhood_id $nid | ccze -A
dic=$(./simplenet-cli device info firewall01 | awk '/"id": / {gsub(/"|,/,"",$2) ; print $2}')
echo

echo "Attaching Vlan to Device"
./simplenet-cli device attach $dic --vlan_id $vid | ccze -A
echo

echo "Listing Devices"
./simplenet-cli device list all | ccze -A
echo

echo "Listing Neighborhoods"
./simplenet-cli neighborhood list all | ccze -A
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
echo

echo "Deleting Vlan"
./simplenet-cli vlan delete $vid
echo

echo "Deleting Neighborhood"
./simplenet-cli neighborhood delete $nid
echo
