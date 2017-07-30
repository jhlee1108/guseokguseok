#!/bin/bash

# Copy configuration files
cd script/
cp class_server.sh.template class_server.sh
cp class_scanner.sh.template class_scanner.sh
cp local_scanner.sh.template local_scanner.sh
cp set_on_monitor_mode.sh.template set_on_monitor_mode.sh

cd ../src/classscanner/
cp class_scanner.ini.template class_scanner.ini

cd ../classserver/
cp class_server.ini.template class_server.ini

cd ../localscanner/
cp local_scanner.ini.template local_scanner.ini

# Install vim
cd ~/
apt-get update
apt-get install -y vim

# vim setting
touch .vimrc
echo set number >> .vimrc
echo set autoindent >> .vimrc
echo set smartindent >> .vimrc
echo set tabstop=4 >> .vimrc
echo set shiftwidth=4 >> .vimrc
echo set expandtab >> .vimrc
echo syntax on >> .vimrc

# Install python 3.5.2
# 1. Install the required build-tools
sudo apt-get install -y build-essential tk-dev
sudo apt-get install -y libncurses5-dev libncursesw5-dev libreadline6-dev
sudo apt-get install -y libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev
sudo apt-get install -y libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev

# 2. Download and install Python 3.5.2
wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
tar zxvf Python-3.5.2.tgz
cd Python-3.5.2
./configure --prefix=/usr/local/opt/python-3.5.2
make -j4
sudo make install

# 3. Make the compiled binaries globally available
sudo ln -s /usr/local/opt/python-3.5.2/bin/pydoc3.5 /usr/bin/pydoc3.5
sudo ln -s /usr/local/opt/python-3.5.2/bin/python3.5 /usr/bin/python3.5
sudo ln -s /usr/local/opt/python-3.5.2/bin/python3.5m /usr/bin/python3.5m
sudo ln -s /usr/local/opt/python-3.5.2/bin/pyvenv-3.5 /usr/bin/pyvenv-3.5
sudo ln -s /usr/local/opt/python-3.5.2/bin/pip3.5 /usr/bin/pip3.5
