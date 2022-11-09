.PHONY: init dev-cluster-up dev-cluster-down install-base-example

init:
	python3 -m pip install --upgrade pip setuptools poetry
	poetry install --with ansible

dev-cluster-up:
	cd multipass && for i in {1..3}; do multipass launch -n node-$${i} --cloud-init cloud-init.yaml --mem 2G --disk 10G --cpus 1; done;

dev-cluster-down:
	for i in {1..3}; do multipass delete -p node-$${i}; done;

install-base-example:
	cd ansible && ANSIBLE_CONFIG=ansible.cfg; poetry run ansible-playbook -vv -kb --ask-become-pass -i inventory.example.yaml base.yaml --limit homelab