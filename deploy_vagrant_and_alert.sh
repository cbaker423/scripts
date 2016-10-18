#!/bin/bash

if [[ $# -lt 2 ]]; then
  echo "USAGE: ./${0##*/} <vagrant_hostname> <inventory_file> [tags]"
  exit
elif [[ $# -ge 3 ]]; then
  hostname=$1
  inventory_file=$2
  tags=$3
else
  hostname=$1
  inventory_file=$2
fi

if [ -z "$tags" ]; then
  vagrant ssh $hostname -c "sudo /bin/ansible-playbook -i /vagrant/inventories/development/$inventory_file /vagrant/playbook/site.yml"; curl http://textbelt.com/text -d number=5124150100 -d "message=Ansible Deployment Complete | EXIT_STATUS: $?"
else
  if [ "$tags" != "notext" ]; then
    vagrant ssh $hostname -c "sudo /bin/ansible-playbook -i /vagrant/inventories/development/$inventory_file /vagrant/playbook/site.yml --tags $tags"; curl http://textbelt.com/text -d number=5124150100 -d "message=Ansible Deployment Complete | EXIT_STATUS: $?"
  else
    vagrant ssh $hostname -c "sudo /bin/ansible-playbook -i /vagrant/inventories/development/$inventory_file /vagrant/playbook/site.yml"
  fi
fi
