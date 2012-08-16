#!/bin/bash -x

echo "Creating"
ngid=$(./simplenet-cli neighborhood create ita01 | sed 's/,\|"//g' | awk '{ print $2 }')
vid=$(./simplenet-cli vlan create vlan01 --neighborhood_id $ngid | sed 's/,\|"//g' | awk '{ print $4 }')
sid=$(./simplenet-cli subnet create 192.168.0.0/24 --vlan_id $vid | sed 's/,\|"//g' | awk '{ print $4 }')
iid=$(./simplenet-cli ip create 192.168.0.1 --subnet_id $sid | sed 's/,\|"//g' | awk '{ print $4 }' )
dic=$(./simplenet-cli device create firewall01 --neighborhood_id $ngid | sed 's/,\|"//g' | awk '{ print $4 }' )
echo

echo "Devices"
./simplenet-cli device info firewall01
./simplenet-cli device list all
./simplenet-cli device attach $dic --vlan_id $vid
echo

echo "Neighborhood"
./simplenet-cli neighborhood info ita01
./simplenet-cli neighborhood list all
echo

echo "Vlan"
./simplenet-cli vlan info vlan01
./simplenet-cli vlan list all
echo

echo "Subnet"
./simplenet-cli subnet info 192.168.0.0/24
./simplenet-cli subnet list all
echo

echo "Ip"
./simplenet-cli ip info 192.168.0.1
./simplenet-cli ip list all
echo

echo "Removing"
./simplenet-cli device detach $dic --vlan_id $vid
./simplenet-cli ip delete $iid
./simplenet-cli subnet delete $sid
./simplenet-cli device delete $dic
./simplenet-cli vlan delete $vid
./simplenet-cli neighborhood delete $ngid
echo
