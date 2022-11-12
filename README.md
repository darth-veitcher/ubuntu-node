# Ubuntu Node

Setup for basic Ubuntu Server nodes, including provisioning for Kubernetes ([MicroK8s](https://microk8s.io)) via [ansible](https://www.ansible.com). Primarily tested on 22.04 LTS as of November 2022 albeit the playbook has been in use in various forms since ~16.04.....

## ℹ️ How to use

You'll need a recent (>=3.7) version of python 🐍 in order to be able to run ansible. If you don't have that head on over to [python.org](https://python.org) and download a compatible version for your platform. Development and testing has been primarily performed on MacOS (both Intel and Apple Silicon) but this should work on most platforms.

### Setup Inventory

The repository ships with an example ansible inventory file. This can be found at `ansible/inventory.example.yaml`.

A simplified version might look as follows. Create your own at `ansible/inventory.yaml` to reflect the machines and variables you'd like to target.

```yaml
all:
  hosts:
    localbox:
      ansible_port: 22 # 22 to begin with then 2222 afterwards
      ansible_host: 192.168.0.234
      ansible_user: adminlocal # ubuntu when fresh, adminlocal afterwards
      ansible_ssh_private_key_file: ~/.ssh/id_rsa
```

### Using the Multipass Quickstart

If you just want to test things out locally, in the [`multipass`](https://multipass.run) folder there's a collection of files to allow you to quickly spin up a 3 node cluster. Simply run `make dev-cluster-up` which, under the hood, calls multipass three times with the `multipass/cloud-init.yaml` configuration to create three identical nodes.

```zsh
➜ multipass list
Name                    State             IPv4             Image
node-1                  Running           192.168.35.8     Ubuntu 22.04 LTS
node-2                  Running           192.168.35.9     Ubuntu 22.04 LTS
node-3                  Running           192.168.35.10    Ubuntu 22.04 LTS
```

_To delete these instances and cleanup run `make dev-cluster-down`._

**NB:** the username/password/keys are contained within the `multipass/cloud-init.yaml` file. You can either import a ssh key from github, use the locally provided one, or roll with plaintext..

The resulting `inventory.yaml` file you need will look something like this based on the above nodes outputted by the `multipass list` command. Adjust as necessary - the below is what is included in the `ansible/inventory.example.yaml` file as a quickstart.

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
        ansible_user: ansible # ansible when fresh, adminlocal afterwards
        ansible_ssh_private_key_file: multipass/admin.id_rsa
        ansible_ssh_common_args: "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -o ControlMaster=auto -o ControlPersist=10m"
```

To run a playbook based on the above inventory you would use the below commands.

**Install ansible** and requirements.

```zsh
# Using Poetry
poetry install --with ansible
# Using pip
python -m pip install -r requirements.txt
```

**Run the provided playbook** against the machines. Make sure to add `poetry run` or activate your virtual environment and run the command from <u>within the `ansible` directory</u> or you will end up with errors such as `ERROR! the playbook: base.yaml could not be found`. <!-- # noqa: MD033 -->

```zsh
# with virtualenv activated
ANSIBLE_CONFIG=ansible.cfg; ansible-playbook -i inventory.yaml base.yaml --limit homelab

# if using poetry
ANSIBLE_CONFIG=ansible.cfg; poetry run ansible-playbook -i inventory.yaml base.yaml --limit homelab
```

NB: If you haven't provided a SSH key for some reason (or your target hosts do not have your key yet), you don't have passwordless sudo etc. you will need to add these using the following ansible command switches:

- `-k`: ask for connection password
- `-b`: run operations with become (will be root)
- `--ask-become-pass`: the password to acquire root for tasks

Eg. `ansible-playbook -kb --ask-become-pass -i inventory.yaml base.yaml --limit homelab`

## Included Roles

### Base

_<subtitle>Update, Harden and Set Sane Defaults</subtitle>_

A Base role exists inside `ansible/roles/base` and is called with the `ansible/base.yaml` playbook.

- Server hardening
  - Creation of non-root administrative user
  - SSH
    - via provided keyfile
    - password disabled
    - limited users to just the specified `deploy_user_name` and/or those included subsequently in the `ssh-users` group on the host
    - change to provided non-standard port
    - disable `X11Forwarding`
    - Increase security levels of SSH using appropriate Ciphers / MACs / Keys
    - Regneration of moduli (optional)
    - Forced MFA for admin account (optional)
  - Firewall with UFW
  - Fail2Ban
- Standard set of utilities I seem to always need
  - wget, curl
  - p7zip
  - nano
  - git
- Avahi mDNS broadcast capabilities for service discovery (optional)

**NB:** Regeneration of the moduli file could take an _**extremely**_ long time depending on the target machine. Use at your own discretion if you feel your threat profile requires it. See [Is it considered worth it to replace OpenSSH's moduli file?](https://security.stackexchange.com/questions/79043/is-it-considered-worth-it-to-replace-opensshs-moduli-file), [OpenSSH moduli](https://entropux.net/article/openssh-moduli/), and [Secure Secure Shell](https://stribika.github.io/2015/01/04/secure-secure-shell.html) for further reading. By default this playbook will disable known insecure keys and ciphers using guidance available from [Mozilla](https://infosec.mozilla.org/guidelines/openssh) as a minimum baseline. Rule of thumb: if you don't have physical control of your hardware **and** you're a literal enemy of a state... you might want to do this... otherwise potentially not 🤷.

## Google Auth

This is an optional role which implements [google-authenticator-libpam](https://github.com/google/google-authenticator-libpam), forcing users to have a multifactor token (TOTP) in order to access the server via ssh and run commands.

⚠️ This will break further use of Ansible workbooks and so use at the end. See [known bug](https://github.com/ansible/ansible/issues/16259) with the use of 2FA and Ansible. ⚠️

To disable it briefly later on edit the ssh service configuration and then restart it:

```
# file: /etc/ssh/sshd_config
Match User {{ your_user_name }}
  AuthenticationMethods publickey
```

The above will allow publickey only authentication over SSH for our ansible user. Remember to remove this and restart the service when finished.

The role will create two files within the `ansible/deploy/{{ inventory_hostname }}` folders associated with the users you've specified in the `ssh_users` group and/or your `deploy_username` variables.

Assuming you've used the `make install-gauth-example` quickstart command:

```zsh
➜ tree ansible/deploy/google-auth

ansible/deploy/google-auth
├── node-1
│   ├── adminlocal-google-auth.png
│   └── adminlocal-google-auth.txt
├── node-2
│   ├── adminlocal-google-auth.png
│   └── adminlocal-google-auth.txt
└── node-3
    ├── adminlocal-google-auth.png
    └── adminlocal-google-auth.txt
```

The .txt file contains the original seed secret and backup codes
The png file is a scannable qr code similar to the below

![qr](assets/adminlocal-google-auth.png)

### MicroK8s

_<subtitle>Initialise Cluster</subtitle>_

Basic usage to install MicroK8s and initialise a cluster with appropriate firewall configuration. Make sure you have setup an appropriate local inventory file containing the details of the servers.

After prepping nodes with a `Base` role we can apply the `MicroK8s` role. This role installs the MicroK8s snap and adds the appropriate firewall rules to allow communication between nodes. Passing `--extra-vars` to this playbook allows you to either `wipe` the kubernetes cluster or `initialise` a new one. See below where we initialise a cluster and allow private networks to access it.

```zsh
export ANSIBLE_CONFIG=ansible.cfg && poetry run ansible-playbook -i inventory.example.yaml microk8s.yaml --limit homelab --extra-vars '{"init_cluster": true, "allow_private_networks": true}'
```

Assuming you've used the quickstart you can login to one of the nodes and get the cluster details.

```zsh
ssh -p 2222 adminlocal@192.168.35.8
```

```zsh
adminlocal@node-1:~$ kubectl get nodes

NAME     STATUS   ROLES    AGE   VERSION
node-1   Ready    <none>   19m   v1.25.3
node-2   Ready    <none>   53s   v1.25.3
node-3   Ready    <none>   63s   v1.25.3
```
