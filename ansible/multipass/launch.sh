#!/bin/bash
for i in {1..3}
do
    multipass launch -n node-${i} --cloud-init cloud-init.yaml --mem 2G --disk 10G --cpus 1
done