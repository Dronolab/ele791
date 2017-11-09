#!/bin/bash

sudo apt-get update

sudo apt-get install libgphoto2-dev python3-dev python3-pip -y

sudo pip3 install -U setuptools
sudo pip3 install -U gphoto2
sudo pip3 install -U inotify