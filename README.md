# Ubuntu Node

Setup for basic Ubuntu Server nodes, including provisioning for Kubernetes via [ansible](https://www.ansible.com). Primarily tested on 21.04 LTS.

## How to use

### Setup Inventory

The repository ships with an example ansible inventory file. This can be found at `ansible/inventory.example.yaml`.

A simplified version might look as follows. Create your own at `ansible/inventory.yaml` to reflect the machines and variables you'd like to target.

### Using the Multipass Quickstart

If you just want to test things out locally, in the `ansible/multipass` folder there's a collection of files to allow you to quickly spin up a 3 node cluster. Simply `cd` into the directory and execute the `launch.sh` script.

```zsh
➜ multipass list                                                                
Name            State             IPv4             Image
node-1          Running           192.168.35.8     Ubuntu 20.04 LTS
node-2          Running           192.168.35.9     Ubuntu 20.04 LTS
node-3          Running           192.168.35.10    Ubuntu 20.04 LTS
```

```yaml
# file: ansible/inventory.yaml
all:
  children:
    homelab:
      hosts:
        node-1:
          ansible_host: 192.168.35.8
        node-2:
          ansible_host: 192.168.35.9
        node-3:
          ansible_host: 192.168.35.10
      vars:
        ansible_port: 22 # 22 when fresh, 2222 afterwards
        ansible_user: ansible  # ansible when fresh, adminlocal afterwards
        ansible_ssh_private_key_file: multipass/admin.id_rsa
        ansible_ssh_common_args: "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -o ControlMaster=auto -o ControlPersist=10m"
```

To run a playbook based on the above inventory you would use the below command:

```zsh
# install virrtualenv with dependencies
cd ansible
poetry install
# from the ansible directory with venv activated
ANSIBLE_CONFIG=ansible.cfg; ansible-playbook -kb --ask-become-pass -i inventory.yaml base.yaml --limit homelab
```

## Included Roles

### Base
*<subtitle>Update, Harden and Set Sane Defaults</subtitle>*

A Base role exists inside `ansible/roles/base` and is called with the `ansible/base.yaml` playbook.

* Server hardening
  * Creation of non-root administrative user
  * SSH
    * via provided keyfile
    * password disabled
    * limited users to just the specified `deploy_user_name`
    * change to provided/random non-standard port (optional)
    * disable `X11Forwarding`
    * Increase security levels of SSH using appropriate Ciphers / MACs / Keys
  * Firewall with UFW
  * Fail2Ban
* Standard set of utilities I seem to always need
  * wget, curl
  * p7zip
  * nano
  * git
* Avahi mDNS broadcast capabilities for service discovery (optional)

### MicroK8s
*<subtitle>Initialise Cluster</subtitle>*

Basic usage to install MicroK8s and initialise a cluster with appropriate firewall configuration. Make sure you have setup an appropriate local inventory file containing the details of the servers.

After prepping nodes with a `Base` role we can apply the `MicroK8s` role. See the kubernetes section (coming soon) for more information.
