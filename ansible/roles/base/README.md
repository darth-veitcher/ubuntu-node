# ansible-base

Basic install and setup of Ubuntu Server. Tested on 16.04.1 LTS through to 20.04.2 LTS

## Intro

This is an automated (semi) ansible role designed to deploy and configure an
Ubuntu Server 16.04 LTS into a base vanilla state with some security measures.

It may work on other platforms but has not been tested.

As an added benefit it has the `ssh_setup.yml` task file which will check for
a valid ssh connection and, based on results, load up the new parameters after
we have locked down and changed ports. This saves us from needing to constantly
change the inventory file.
