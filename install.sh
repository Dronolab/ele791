#!/bin/bash


sudo apt-get update -y
sudo apt-get --assume-yes install  libboost-all-dev
sudo apt-get --assume-yes install  exiv2
sudo apt-get --assume-yes install  python-all-dev
sudo apt-get --assume-yes install  scons
sudo apt-get --assume-yes install  libexiv2-dev
sudo apt-get --assume-yes install  libboost-python-dev
sudo apt-get --assume-yes install  libgphoto2-dev
sudo apt-get --assume-yes install  python3
sudo apt-get --assume-yes install  python3-pip
sudo apt-get --assume-yes install  python-dev

sudo pip3 install -r requirement.txt