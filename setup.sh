#!/bin/bash

# Copy configuration files
cd script/
cp class_scanner.sh.template class_scanner.sh
cp local_scanner.sh.template local_scanner.sh
cp set_on_monitor_mode.sh.template set_on_monitor_mode.sh
cp class_server.sh.template class_server.sh

cd ../src/classscanner/
cp class_scanner.ini.template class_scanner.ini

cd ../classserver/
cp class_server.ini.template class_server.ini

cd ../localscanner/
cp local_scanner.ini.template local_scanner.ini

# Install python 3.6
cd ~/
apt-get update
apt-get install -y vim
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz
tar xzvf Python-3.6.0.tgz
cd Python-3.6.0/
apt-get install libsqlite3-dev
./configure --enable-loadable-sqlite-extensions && make && sudo make install

