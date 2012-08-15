#!/bin/bash -x

ngid=$(./simplenet-cli neighborhood create ncode | sed 's/,\|"//g' | awk '{ print $2 }')
vid=$(./simplenet-cli vlan create vlan01 --neighborhood_id | sed 's/,\|"//g' | awk '{ print $4 }')
sid=$(./simplenet-cli subnet create 192.168.0.0/24 --vlan_id $vid | sed 's/,\|"//g' | awk '{ print $4 }')

./simplenet-cli neighborhood info ncode
./simplenet-cli neighborhood list all

./simplenet-cli vlan info vlan01
./simplenet-cli vlan list all

./simplenet-cli subnet info 192.168.0.0/24
./simplenet-cli subnet list all

./simplenet-cli vlan delete $vid
./simplenet-cli neighborhood delete $ngid
./simplenet-cli subnet delete $sid
