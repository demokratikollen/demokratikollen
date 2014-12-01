#!/bin/bash
#
# Windows shell provisioner for Ansible playbooks, based on KSid's
# windows-vagrant-ansible: https://github.com/KSid/windows-vagrant-ansible
#
# @todo - Allow proxy configuration to be passed in via Vagrantfile config.
#
# @see README.md
# @author Jeff Geerling, 2014
# @version 1.0
#

# Uncomment if behind a proxy server.
# export {http,https,ftp}_proxy='http://username:password@proxy-host:80'

ANSIBLE_PLAYBOOK=$1

if [ ! -f /vagrant/$ANSIBLE_PLAYBOOK ]; then
  echo "Cannot find Ansible playbook."
  exit 1
fi

# Install Ansible and its dependencies if it's not installed already.
if [ ! -f /usr/local/bin/ansible ]; then
  echo "Installing Ansible dependencies."
  sudo apt-get update
  sudo apt-get -y install python python-dev
  echo "Installing pip via easy_install."
  wget http://peak.telecommunity.com/dist/ez_setup.py
  sudo python ez_setup.py && rm -f ez_setup.py
  sudo easy_install pip
  # Make sure setuptools are installed correctly.
  sudo pip install setuptools --no-use-wheel --upgrade
  echo "Installing required python modules."
  sudo pip install paramiko pyyaml jinja2 markupsafe
  echo "Installing Ansible."
  sudo pip install ansible==1.7
fi

# Fix the ansible host file to be able to only do the develop provisioning
if [ ! -f /tmp/ansible_hosts ] ; then
  sudo echo "localhost ansible_connection=local" >> /tmp/ansible_hosts
  sudo echo "[develop]" >> /tmp/ansible_hosts
  sudo echo "localhost" >> /tmp/ansible_hosts
fi

echo "Running Ansible provisioner defined in Vagrantfile."
ansible-playbook /vagrant/${ANSIBLE_PLAYBOOK} -i /tmp/ansible_hosts --extra-vars "is_windows=true"

